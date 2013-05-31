import rhinoscriptsyntax as rs
import random, math, time
import Rhino
import scriptcontext
import sys
import itertools
import System.Guid

import rhino_helpers
reload(rhino_helpers)
from rhino_helpers import *

import matTrussToMesh
reload(matTrussToMesh)
from matTrussToMesh import *

def loadExampleMesh():

	rawNodes,rawEdges = importTrussData()
	mesh,mesh_id = constructMesh(rawNodes,rawEdges)

	return mesh,mesh_id

def unwrapExampleMesh():
	mesh,mesh_id = loadExampleMesh()
	unwrap(mesh,mesh_id)


def unwrap(mesh,mesh_id):

	faces,edge_weights,thetaMax = getDual(mesh)
	#displayDual(faces,edge_weights,thetaMax,mesh)
	#displayFaceIdxs(mesh)
	#displayNormals(mesh)
	foldList = getSpanningKruskal(faces,edge_weights,mesh)

	#displayCutEdges(foldList,mesh,True)
	#displayFoldEdges(foldList,mesh,True)

	flatEdgeCoords = [None]*mesh.TopologyEdges.Count

	origin = rs.WorldXYPlane()
	faceIdx = 0
	edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
	tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
	#fromBasis = getBasisOnMesh(faceIdx,edgeIdx,tVertIdx,mesh)
	toBasis = origin

	#displayOrthoBasis(fromBasis,faceIdx)
	#displayOrthoBasis(toBasis,faceIdx)

	flatEdgeCoords = layoutFace(0,faceIdx,edgeIdx,tVertIdx,foldList,mesh,toBasis,flatEdgeCoords)
	print "flatEdgeCoords:"
	print flatEdgeCoords[47]
	

	print('Version:')
	print(sys.version )



"""FLATTEN/LAYOUT"""

def layoutFace(rc,faceIdx,edgeIdx,tVertIdx,foldList,mesh,toBasis,flatEdgeCoords):
	''' Recurse through faces, moving along fold edges
	'''
	
	fromBasis = getBasisOnMesh(faceIdx,edgeIdx,tVertIdx,mesh)
	faceEdges = getFaceEdges(faceIdx,mesh)
	xForm = createTransformMatrix(fromBasis,toBasis)

	spaces = " | "*rc
	listStr = "[%02d,%02d,%02d]"%(faceEdges[0],faceEdges[1],faceEdges[2])
	print spaces + listStr


	for testEdgeIdx in faceEdges:
		newCoords = assignNewPntsToEdge(xForm,testEdgeIdx,mesh)
		line = Rhino.Geometry.Line(newCoords[0],newCoords[1])

		addEdgeLegal = isLegalToAddEdge(newCoords,testEdgeIdx,flatEdgeCoords,foldList,mesh)

		if testEdgeIdx == 47:
			print "47!!"
			print "edgeLegality: " + str(addEdgeLegal)
			print str(testEdgeIdx in foldList)
			print str(flatEdgeCoords[testEdgeIdx])
			print str(flatEdgeCoords[47])

		if testEdgeIdx in foldList:

			drawLine(line,testEdgeIdx,isFoldEdge=True,displayIdx=True)

			if addEdgeLegal:
				flatEdgeCoords.insert(testEdgeIdx,newCoords)

				if testEdgeIdx == 47:
					print "added at 47"

				newFaceIdx = getOtherFaceIdx(testEdgeIdx,faceIdx,mesh)
				newEdgeIdx = testEdgeIdx
				newTVertIdx = mesh.TopologyEdges.GetTopologyVertices(testEdgeIdx).I #convention: useI
				newToBasis = getBasisFlat(newCoords)
				#newFromBasis = getBasisOnMesh(newFaceIdx,testEdgeIdx,newTVertIdx,mesh)
				#displayOrthoBasis(newToBasis,newFaceIdx)
				#displayOrthoBasis(newFromBasis,newFaceIdx)

				flatEdgeCoords = layoutFace(rc+1,newFaceIdx,newEdgeIdx,newTVertIdx,foldList,mesh,newToBasis,flatEdgeCoords)
			
		elif testEdgeIdx not in foldList:
			drawLine(line,testEdgeIdx,isFoldEdge=False,displayIdx=True)
			flatEdgeCoords.insert(testEdgeIdx,newCoords)
	
	return flatEdgeCoords

def drawLine(line,edgeIdx,isFoldEdge,displayIdx):
	if isFoldEdge:
		#GREEN for foldEdge
		attrCol = setAttrColor(0,49,224,61)
	else:
		#RED for cutEdge
		attrCol = setAttrColor(0,237,43,120)

	scriptcontext.doc.Objects.AddLine(line,attrCol)

	if displayIdx:
		displayEdgeIdx(line,edgeIdx)


def isLegalToAddEdge(newCoords,edgeIdx,flatEdgeCoords,foldList,mesh):
	#WTF!!!!!!!!!
	if flatEdgeCoords[edgeIdx] == None:
			return True
	elif edgeIdx in foldList:
		assert(len(flatEdgeCoords[edgeIdx])==2)
		if(flatEdgeCoords[edgeIdx]==newCoords):
			return False
		if(flatEdgeCoords[edgeIdx]==newCoords.reverse()):
			return False
	elif edgeIdx not in foldList:
		if len(flatEdgeCoords[edgeIdx])==4:
			return False
		else:
			return True
	else:
		print "######################"
		print "error: %d coords assigned to edge %d"%len(flatEdgeCoords[edgeIdx])%edgeIdx
		return None
		

def getBasisFlat(newCoords):
	#Convention: always use .I element from the tVerts associated with a given edge
	o = newCoords[0]
	#assert(o.Z==0), "newCoord has Z compenent!"
	#print "o.z:%1.2f"%o.Z
	x = Rhino.Geometry.Vector3d(newCoords[1]-newCoords[0])
	x.Unitize()
	z = rs.WorldXYPlane()[3]
	#z = Rhino.Geometry.Vector3d(0.0,0.0,1.0)
	z.Unitize()
	y = Rhino.Geometry.Vector3d.CrossProduct(z,x)
	y.Unitize()

	assert(x.Length-1<.00000001), "x.Length!~=1"
	assert(y.Length-1<.00000001), "y.Length!~=1"
	assert(z.Length-1<.00000001), "z.Length!~=1"

	return [o,x,y,z]

 
def getOtherFaceIdx(edgeIdx,faceIdx,mesh):
	connectedFaces = convertArray(mesh.TopologyEdges.GetConnectedFaces(edgeIdx))
	assert(len(connectedFaces)==2),"getOtherFaceIdx(): more than two faces connecting an edge"
	assert(faceIdx in connectedFaces),"getOtherFaceIdx(): faceIdx not in faces associated with edge"

	#eventually probably need to relax this condition for more complex trusses
	newFaceIdx = None
	if (connectedFaces[0]==faceIdx):
		newFaceIdx = connectedFaces[1]
	elif (connectedFaces[1]==faceIdx):
		newFaceIdx = connectedFaces[0]
	else:
		print "problem in getOtherFaceIdx: edgeIdx not in faceIdx,assert should have caught error"
		return None

	assert(newFaceIdx!=faceIdx), "getOtherFaceIdx(): newFaceIdx == faceIdx!"
	return newFaceIdx

def assignNewPntsToEdge(xForm,edgeIdx,mesh):
	#output: list of new coords, Point3f
	indexPair = mesh.TopologyEdges.GetTopologyVertices(edgeIdx)
	idxI = indexPair.I
	idxJ = indexPair.J
	pI = mesh.TopologyVertices.Item[idxI]
	pJ = mesh.TopologyVertices.Item[idxJ]
	pI.Transform(xForm)
	pJ.Transform(xForm)
	#assert(pI.Z == 0), "pI.Z!=0"
	#assert(pJ.Z == 0), "pJ.Z!=0"
	return [pI,pJ]

def createTransformMatrix(fromBasis,toBasis):
	p = fromBasis[0]
	u = fromBasis[1]
	v = fromBasis[2]
	w = fromBasis[3]

	o = toBasis[0]
	i = toBasis[1]
	j = toBasis[2]
	k = toBasis[3]
	
	o = Rhino.Geometry.Vector3d(o)
	p = Rhino.Geometry.Vector3d(p)
	
	changeBasisXform = Rhino.Geometry.Transform.ChangeBasis(u,v,w,i,j,k)

	transFormToOrigin = Rhino.Geometry.Transform.Translation(-p)
	rotatXform = Rhino.Geometry.Transform.Rotation(u,v,w,i,j,k)
	transFormToPnt = Rhino.Geometry.Transform.Translation(o)
	xForm1 = Rhino.Geometry.Transform.Multiply(rotatXform,transFormToOrigin)
	xForm2 = Rhino.Geometry.Transform.Multiply(transFormToPnt,xForm1)

	transXform = Rhino.Geometry.Transform.Translation(o-p)
	fullXform = Rhino.Geometry.Transform.Multiply(rotatXform,transXform)

	return xForm2

def getBasisOnMesh(faceIdx,edgeIdx,tVertIdx,mesh):
	faceTopoVerts = convertArray(mesh.Faces.GetTopologicalVertices(faceIdx))
	assert(tVertIdx in faceTopoVerts),"prblm in getBasisOnMesh():tVert not in faceTopoVerts "
	edgeTopoVerts = [mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I,mesh.TopologyEdges.GetTopologyVertices(edgeIdx).J]
	assert(tVertIdx in edgeTopoVerts),"prblm in getBasisOnMesh():tVert not part of given edge"
	def getOther(tVertIdx,edgeTopoVerts):
		if(edgeTopoVerts[0]==tVertIdx):
			return edgeTopoVerts[1]
		elif(edgeTopoVerts[1]==tVertIdx):
			return edgeTopoVerts[0]
		else:
			print "ERROR: edgeTopoVerts does not contain tVertIdx"
			return None

	"""U"""
	p1 = mesh.TopologyVertices.Item[tVertIdx]
	p2 = mesh.TopologyVertices.Item[getOther(tVertIdx,edgeTopoVerts)]
	
	pU = p2-p1
	u = Rhino.Geometry.Vector3d(pU)
	u.Unitize()

	"""W"""
	w = Rhino.Geometry.Vector3d(mesh.FaceNormals.Item[faceIdx])
	w.Unitize()

	"""V"""
	v = Rhino.Geometry.Vector3d.CrossProduct(w,u)
	v.Unitize()

	"""P"""
	p = mesh.TopologyVertices.Item[tVertIdx]

	return [p,u,v,w]

def displayOrthoBasis(basis,faceIdx):
	p = basis[0]
	u = basis[1]
	v = basis[2]
	w = basis[3]
	
	assert(u.Length-1<.00000001), "u.Length!~=1"
	assert(v.Length-1<.00000001), "v.Length!~=1"
	assert(w.Length-1<.00000001), "w.Length!~=1"
	basisGeom = []
	"""U: BLUE"""
	attrU = setAttrColor(0,10,103,163)
	attrU.ObjectDecoration = Rhino.DocObjects.ObjectDecoration.EndArrowhead
	uLine = Rhino.Geometry.Line(p,u)
	textPnt = Rhino.Geometry.Point3d.Add(p,u)
	uText = Rhino.Geometry.TextDot("u",textPnt)
	basisGeom.append(scriptcontext.doc.Objects.AddTextDot(uText,attrU))
	basisGeom.append(scriptcontext.doc.Objects.AddLine(uLine,attrU))
	"""V: YELLOW"""
	attrV = setAttrColor(0,255,188,0)
	attrV.ObjectDecoration = Rhino.DocObjects.ObjectDecoration.EndArrowhead
	vLine = Rhino.Geometry.Line(p,v)
	textPnt = Rhino.Geometry.Point3d.Add(p,v)
	vText = Rhino.Geometry.TextDot("v",textPnt)
	basisGeom.append(scriptcontext.doc.Objects.AddTextDot(vText,attrV))
	basisGeom.append(scriptcontext.doc.Objects.AddLine(vLine,attrV))
	"""W: PAPAYA"""
	attrW = setAttrColor(0,255,65,0)
	attrW.ObjectDecoration = Rhino.DocObjects.ObjectDecoration.EndArrowhead
	wLine = Rhino.Geometry.Line(p,w)
	textPnt = Rhino.Geometry.Point3d.Add(p,w)
	wText = Rhino.Geometry.TextDot("w",textPnt)
	basisGeom.append(scriptcontext.doc.Objects.AddTextDot(wText,attrW))
	basisGeom.append(scriptcontext.doc.Objects.AddLine(wLine,attrW))
	
	grpStr = "face" + str(faceIdx)

	createGroup(grpStr,basisGeom)


def getSpanningKruskal(faces,edge_weights,mesh):

	'''
	note: have not considered open mesh, or non-manifold edges
	input:
		faces = list of faces in mesh. necessary?
		edge_weights = list of tuples elem0 = edgeIdx, elem1 = weight
	output:
		foldList = list of edgeIdx's that are to be cut
	'''
	treeSets = []
	foldList = []
	for tupEdge in edge_weights:
		edgeIdx = tupEdge[0]
		arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIdx)
		setConnFaces = set([arrConnFaces.GetValue(0),arrConnFaces.GetValue(1)])


		parentSets = []
		#print"edgeSet:"
		#print setConnFaces
		isLegal = True
		for i, treeSet in enumerate(treeSets):
			if setConnFaces.issubset(treeSet):
				#print"--was illegal"
				isLegal = False
				break
			elif not setConnFaces.isdisjoint(treeSet):
					#print"overlapped"
					parentSets.append(i)

		if isLegal==True:
			foldList.append(edgeIdx)
			if len(parentSets) == 0:
				treeSets.append(setConnFaces)
			elif len(parentSets) == 1:
				treeSets[parentSets[0]].update(setConnFaces)
			elif len(parentSets) == 2:
				treeSets[parentSets[0]].update(treeSets[parentSets[1]])
				treeSets.pop(parentSets[1])
			elif len(parentSets)>2:
				print"Error in m.s.t: more than two sets overlapped with edgeSet!"
				print "len parentSets: %d\n" %len(parentSets)
				print(treeSets)
				print(parentSets)
				print(setConnFaces)
				

		# wow there must be a cleaner way of doing this!!! some set tricks
		# also the if staements could be cleaned up probs.
	return foldList

"""FOLD DISPLAY"""
def displayFoldEdges(foldList,mesh,displayIdx):
	foldLines = []
	#DARK GREEN foldEdge
	attr = setAttrColor(0,25,145,33)
	for i in range(mesh.TopologyEdges.Count):
		if i in foldList:
			line = getLineForTEdge(i,mesh)
			foldLines.append(scriptcontext.doc.Objects.AddLine(line,attr))
			if displayIdx:
				displayEdgeIdx(line,i)

	createGroup("foldLines",foldLines)

def displayCutEdges(foldList,mesh,displayIdx):
	cutLines = []
	# RED cutEdge
	attr= setAttrColor(0,237,17,53)
	for i in range(mesh.TopologyEdges.Count):
		if i not in foldList:
			line = getLineForTEdge(i,mesh)
			cutLines.append(scriptcontext.doc.Objects.AddLine(line,attr))
			if displayIdx:
				displayEdgeIdx(line,i)
	createGroup("cutLines",cutLines)

def getLineForTEdge(edgeIdx,mesh):
	tVerts = mesh.TopologyEdges.GetTopologyVertices(edgeIdx)
	p1 = mesh.TopologyVertices.Item[tVerts.I]
	p2 = mesh.TopologyVertices.Item[tVerts.J]
	return Rhino.Geometry.Line(p1,p2)


"""chang name to assign edgeWeights, implicit in methods available for topoEdges"""
def getDual(mesh):
	'''
	input: 
		mesh = instance of Rhino.Geometry.Mesh()
	ouput:
		faces = list of Faces as MeshFace class (4.rhino3d.com/5/rhinocommon/)
		connFaces = list of tuples (edgeIdx,weight)
	'''
	faces = []
	thetaMax = -1
	for i in range(mesh.Faces.Count):
		faces.append(mesh.Faces.GetFace(i))
	edge_weights = []
	for i in range(mesh.TopologyEdges.Count):
		arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(i)

		f0 = arrConnFaces.GetValue(0)
		f1 = arrConnFaces.GetValue(1)
		angWeight = calculateAngle(arrConnFaces,mesh)
		if angWeight > thetaMax:
			thetaMax = angWeight
		edge_weights.append((i,angWeight))
		#connFaces.append(tupleConnFaces)
	edge_weights = sorted(edge_weights,key=lambda tup: tup[1],reverse=False)
	#how to reverse order of sorting??

	
	#pretty2DListPrint(edge_weights)

	return faces,edge_weights,thetaMax

def pretty2DListPrint(array):
	print "\n".join(" ".join(map(str, line)) for line in array)


def calculateAngle(arrConnFaces,mesh):
	faceIdx0 = arrConnFaces.GetValue(0)
	faceIdx1 = arrConnFaces.GetValue(1)

	faceNorm0 = mesh.FaceNormals.Item[faceIdx0]
	faceNorm1 = mesh.FaceNormals.Item[faceIdx1]

	return rs.VectorAngle(faceNorm0,faceNorm1) #returns None on error


def checkGetBasisOnMesh(mesh):
	'''
	arbitraty edge is chosen, so this method is only to see that getBasisOnMesh is working
	HAVE NOT TESTED YET
	'''
	for faceIdx in range(mesh.Faces.Count):
	#face = mesh.Faces.Item[i]
		edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
		tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
		basis= getBasisOnMesh(faceIdx,edgeIdx,tVertIdx,mesh)
		displayOrthoBasis(basis)
	





if __name__=="__main__":
	unwrapExampleMesh()