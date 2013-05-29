import rhinoscriptsyntax as rs
import random, math, time
import Rhino
import scriptcontext
import sys
import itertools
import System.Guid
import System.Drawing


def unwrapper():
	nodeCsvFile = open('trussNodes.csv','rb')
	nodeLines = nodeCsvFile.readlines()
	nodeCsvFile.close()

	rawNodes = []

	for line in nodeLines:
		tokens = line.split(',')
		pnt = [float(item) for item in tokens]
		#rs.AddPoint( pnt)
		rawNodes.append(pnt)

	edgeCsvFile = open('trussEdges.csv','rb')
	edgeLines = edgeCsvFile.readlines()
	edgeCsvFile.close()

	rawEdges = []

	for line in edgeLines:
		tokens = line.split(',')
		edge = [int(item) for item in tokens]
		idx1 = edge[0]-1 #matlab is 1-indexed!
		idx2 = edge[1]-1
		#p1 = rawNodes[idx1] 
		#p2 = rawNodes[idx2]
		#rs.AddLine(p1,p2)
		rawEdges.append([idx1,idx2])

	nodes = createGraph(rawNodes,rawEdges)
	#print"lenNodes: %d" %len(nodes)
	#print"lenRawNodes: %d" %len(rawNodes)
	polylineCoords,faces = getTriangleCoords(nodes)

	mesh_id,mesh = generateMesh(rawNodes,faces)
	faces,edge_weights,thetaMax = getDual(mesh)
	displayDual(faces,edge_weights,thetaMax,mesh)

	foldList = getSpanningKruskal(faces,edge_weights,mesh)
	displayCutEdges(foldList,mesh)
	#displayNormals(mesh)


	# for i in range(mesh.Faces.Count):
	# 	#face = mesh.Faces.Item[i]
	# 	edgeIdx = mesh.TopologyEdges.GetEdgesForFace(i).GetValue(0)
	# 	tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).J
	# 	u,v,w,p = getOrthoBasis(i,edgeIdx,tVertIdx,mesh)
	# 	displayOrthoBasis(u,v,w,p)
	i = 3
	edgeIdx = mesh.TopologyEdges.GetEdgesForFace(i).GetValue(0)
	tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).J
	u,v,w,p = getOrthoBasis(i,edgeIdx,tVertIdx,mesh)
	displayOrthoBasis(u,v,w,p)
	origin = rs.WorldXYPlane()
	print "worldOrigin:"
	print origin[0]
	xForm = createTransformMatrix(origin[1],origin[2],origin[3],origin[0],u,v,w,p)
	getrc,p0,p1,p2,p3 = mesh.Faces.GetFaceVertices(i)
	pnts = [p0,p1,p2]
	for i, pnt in enumerate(pnts):
		#print type(pnt)
		pnt.Transform(xForm)
		rs.AddPoint(pnt)
	rs.AddPolyline(pnts)
	


	print('Version:')
	print(sys.version )

def displayNormals(mesh):
	normLines = []
	for i in range(mesh.FaceNormals.Count):
		p1 = mesh.Faces.GetFaceCenter(i)
		p2 = p1 + mesh.FaceNormals.Item[i]
		normLines.append(rs.AddLine(p1,p2))
	createGroup("normLines",normLines)

def displayDual(faces,edge_weights,thetaMax,mesh):
	medianEdgeLen = getMedianEdgeLen(mesh)
	aspectRatio = 1/10.0
	scaleFactor = medianEdgeLen*aspectRatio
	dualRods = []
	for tupEdge in edge_weights:
		edgeIdx = tupEdge[0]
		weight = tupEdge[1]
		r = (weight/thetaMax)*scaleFactor
		connFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIdx)
		faceCenter0 = mesh.Faces.GetFaceCenter(connFaces.GetValue(0))
		faceCenter1 = mesh.Faces.GetFaceCenter(connFaces.GetValue(1))

		dualRods.append(rs.AddCylinder(faceCenter0,faceCenter1,r))
	createGroup("dualRods",dualRods)
		


def createGroup(groupName,objects):
	name = rs.AddGroup(groupName)
	if not rs.AddObjectsToGroup(objects,groupName):
		print "failed to group"

def getMedianEdgeLen(mesh):
	edgeLens = getEdgeLengths(mesh)
	return getMedian(edgeLens)

def getEdgeLengths(mesh):
	edgeLens = []
	for i in range(mesh.TopologyEdges.Count):
		edgeLine = mesh.TopologyEdges.EdgeLine(i)
		edgeLen = edgeLine.Length
		edgeLens.append(edgeLen)
	return edgeLens

def getEdgeLen(edgIdx,mesh):
	edgeLine = mesh.TopologyEdges.EdgeLine(edgeIdx)
	return edgeLine.Length

def getMedian(edgeLens):
	eLensSorted = sorted(edgeLens)
	nEdges = len(edgeLens)
	assert(nEdges>0), "nEdges is !>0, error in getMedianEdgeLen()"
	if nEdges%2 ==0:
		idxUpper = nEdges/2
		idxLower = idxUpper-1
		avg = (edgeLens[idxUpper]+edgeLens[idxLower])/2.0
		return avg
	else:
		return edgeLens[int(nEdges/2)]

def assignFlatCoordsToEdges(foldList,mesh):
	flattenedEdgeCoords = [None]*mesh.TopologyEdges.Count 
	#each rowIdx coressponds to a edge in TopologyEdges
	randFaceIdx = random.randint(0,mesh.Faces.Count-1)
	rs.AddTextDot("FirstFace",mesh.Faces.GetFaceCenter(randFaceIdx))
	topoEdges = mesh.TopologyEdges.GetEdgesForFace(randFaceIdx)
	for i, topoEdge in enumerate(topoEdges):
		if i==0:
			v1 = Rhino.Geometry.Vector2f(0.0,0.0)
			edgeLen = getEdgeLen(edgeIdx,mesh)
			v2 = Rhino.Geometry.Vector2f(0.0,edgeLen)
			flattenedEdgeCoords.insert(i,[v1,v2])
		elif i==1:
			pass

def createTransformMatrix(i,j,k,o,u,v,w,p):
	# i = Rhino.Geometry.Vector3d(1.0,0.0,0.0)
	# j = Rhino.Geometry.Vector3d(0.0,1.0,0.0)
	# k = Rhino.Geometry.Vector3d(0.0,0.0,1.0)
	o = Rhino.Geometry.Vector3d(o)
	p = Rhino.Geometry.Vector3d(p)
	rotatXform = Rhino.Geometry.Transform.Rotation(u,v,w,i,j,k)
	transXform = Rhino.Geometry.Transform.Translation(o-p)
	fullXform = Rhino.Geometry.Transform.Multiply(rotatXform,transXform)
	#matrix = Rhino.Geometry.Matrix(fullXform)
	return fullXform




def getOrthoBasis(faceIdx,edgeIdx,tVertIdx,mesh):
	faceTopoVerts = convertArray(mesh.Faces.GetTopologicalVertices(faceIdx))
	assert(tVertIdx in faceTopoVerts),"prblm in getOrthoBasis():tVert not in faceTopoVerts "
	edgeTopoVerts = [mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I,mesh.TopologyEdges.GetTopologyVertices(edgeIdx).J]
	assert(tVertIdx in edgeTopoVerts),"prblm in getOrthoBasis():tVert not part of given edge"
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

	return u,v,w,p

def displayOrthoBasis(u,v,w,p):
	assert(u.Length-1<.00000001), "u.Length!~=1"
	assert(v.Length-1<.00000001), "v.Length!~=1"
	assert(w.Length-1<.00000001), "w.Length!~=1"
	basis = []
	"""U: BLUE"""
	attrU = setAttrColor(0,10,103,163)
	attrU.ObjectDecoration = Rhino.DocObjects.ObjectDecoration.EndArrowhead
	uLine = Rhino.Geometry.Line(p,u)
	basis.append(scriptcontext.doc.Objects.AddLine(uLine,attrU))
	"""V: YELLOW"""
	attrV = setAttrColor(0,255,188,0)
	attrV.ObjectDecoration = Rhino.DocObjects.ObjectDecoration.EndArrowhead
	vLine = Rhino.Geometry.Line(p,v)
	basis.append(scriptcontext.doc.Objects.AddLine(vLine,attrV))
	"""W: PAPAYA"""
	attrW = setAttrColor(0,255,65,0)
	attrW.ObjectDecoration = Rhino.DocObjects.ObjectDecoration.EndArrowhead
	wLine = Rhino.Geometry.Line(p,w)
	basis.append(scriptcontext.doc.Objects.AddLine(wLine,attrW))
	
	createGroup("basis",basis)

def setAttrColor(a,r,g,b):
	attr = Rhino.DocObjects.ObjectAttributes()
	attr.ObjectColor = System.Drawing.Color.FromArgb(a,r,g,b)
	attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
	return attr

def convertArray(array):
	pyList = []
	for i in range(array.Length):
		pyList.append(array.GetValue(i))
	return pyList


def getSpanningKruskal(faces,edge_weights,mesh):
	#note: have not considered open mesh, or non-manifold edges
	#input:
	#	faces = list of faces in mesh. necessary?
	#	edge_weights = list of tuples elem0 = edgeIdx, elem1 = weight
	#output:
	#	foldList = list of edgeIdx's that are to be cut
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
			else:
				pass
				#print"not subset, isdisjoint"

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


def displayFoldEdges(foldList,mesh):
	foldLines = []
	for edgeIdx in foldList:
		foldLines.append(addLineForTEdge(edgeIdx,mesh))
	createGroup("foldLines",foldLines)

def displayCutEdges(foldLines,mesh):
	cutLines = []
	for i in range(mesh.TopologyEdges.Count):
		if i not in foldLines:
			cutLines.append(addLineForTEdge(i,mesh))
	createGroup("cutLines",cutLines)

def getKeyForMaxVal(edge_weights,medge_set):
	pass

def addLineForTEdge(edgeIdx,mesh):
	tVerts = mesh.TopologyEdges.GetTopologyVertices(edgeIdx)
	p1 = mesh.TopologyVertices.Item[tVerts.I]
	p2 = mesh.TopologyVertices.Item[tVerts.J]
	return rs.AddLine(p1,p2)



def getDual(mesh): #unnecesary, implicit in methods available for topoEdges
	#input: 
	#	mesh
	#ouput:
	#	faces = list of Faces as MeshFace class (4.rhino3d.com/5/rhinocommon/)
	#	connFaces = list of tuples (edgeIdx,weight)
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

	
	pretty2DListPrint(edge_weights)

	return faces,edge_weights,thetaMax

def pretty2DListPrint(array):
	print "\n".join(" ".join(map(str, line)) for line in array)


def calculateAngle(arrConnFaces,mesh):
	faceIdx0 = arrConnFaces.GetValue(0)
	faceIdx1 = arrConnFaces.GetValue(1)

	faceNorm0 = mesh.FaceNormals.Item[faceIdx0]
	faceNorm1 = mesh.FaceNormals.Item[faceIdx1]

	return rs.VectorAngle(faceNorm0,faceNorm1) #returns None on error



def generateMesh(rawNodes,faces):
	mesh = Rhino.Geometry.Mesh()
	for node in rawNodes:
		mesh.Vertices.Add(node[0],node[1],node[2])
	for face in faces:
		mesh.Faces.AddFace(face[0],face[1],face[2])

	mesh.UnifyNormals()
	mesh.Normals.ComputeNormals()
	mesh.Compact()
	mesh_id = scriptcontext.doc.Objects.AddMesh(mesh)
	if mesh_id !=System.Guid.Empty:
		scriptcontext.doc.Views.Redraw()
		return mesh_id,mesh
	return Rhino.Commands.Result.Failure


class Node():
	hasBeenCenter = False
	def __init__(self,coord,neighbors,edges):
		self.coord = coord
		self.X = coord[0]
		self.Y = coord[1]
		self.Z = coord[2]
		self.neighbors = neighbors
		self.edges = edges

	def draw(self):
		rs.AddPoint(self.X,self.Y,self.Z)

def getTriangleCoords(nodes):
	# this is the clique problem!
	polylineCoords = []
	faces = []
	for i, node in enumerate(nodes):
		edges = node.edges
		node.hasBeenCenter = True

		touchedNeighbors = []
		for neighIdx in node.neighbors:
			node2 = nodes[neighIdx]
			touchedNeighbors.append(neighIdx)

			if(not node2.hasBeenCenter):
				for nnIdx in node2.neighbors:
					node3 = nodes[nnIdx]

					if(not node3.hasBeenCenter and nnIdx not in touchedNeighbors):				
						if nnIdx in node.neighbors and nnIdx!=i:
							polylineCoords.append([node.coord,node2.coord,node3.coord,node.coord])
							faces.append([i,neighIdx,nnIdx])
	

	return polylineCoords, faces

def removeDups(list2D):
	#stackoverflow.com/questions/2213923/python-removing-duplicates-from-a-list-of-lists
	return list(k for k,_ in itertools.groupby(list2D))


def createGraph(rawNodes,rawEdges):
	nodes = []
	for i, coord in enumerate(rawNodes):
		#print i 
		neighbors,edges = findNeighbors(i,rawEdges)
		#if neighbors:
		node = Node(coord,neighbors,edges)
		nodes.append(node)
	return nodes

def findNeighbors(i,rawEdges):
	neighbors = []
	edges = []
	for edge in rawEdges:
		if(i in edge):
			edges.append(edge)
			idx = edge.index(i)
			#print(idx)
			if (idx == 0):
				neighbors.append(edge[1])
			elif (idx ==1):
				neighbors.append(edge[0])
	return neighbors,edges

test_rawEdges = [[1,2],[3,4],[2,4],[1,5],[2,100]]
tNeighbors,tEdges = findNeighbors(1,test_rawEdges)
assert(tNeighbors==[2,5] and tEdges==[[1,2],[1,5]]), "problem in findNeighbors"
#print(test_neighbors)






if __name__=="__main__":
	unwrapper()