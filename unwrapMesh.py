import rhinoscriptsyntax as rs
import random, math, time
import Rhino
import scriptcontext
import sys
import itertools
import System.Guid

import transformations
reload(transformations)
from transformations import *

import rhino_helpers
reload(rhino_helpers)
from rhino_helpers import *

import visualization
reload(visualization)
from visualization import *

import matTrussToMesh
reload(matTrussToMesh)
from matTrussToMesh import *

import flat_edge
reload(flat_edge)
from flat_edge import FlatEdge

def loadExampleMesh():

	rawNodes,rawEdges = importTrussData()
	mesh,mesh_id = constructMesh(rawNodes,rawEdges)

	return mesh,mesh_id

def unwrapExampleMesh():
	mesh,mesh_id = loadExampleMesh()
	unwrap(mesh,mesh_id)


def unwrap(mesh,mesh_id):
	faces,edge_weights,thetaMax = assignEdgeWeights(mesh)
	foldList = getSpanningKruskal(faces,edge_weights,mesh)

	flatEdges = [list() for _ in xrange(mesh.TopologyEdges.Count)]

	origin = rs.WorldXYPlane()
	faceIdx = 0
	edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
	tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
	initBasisInfo = (faceIdx,edgeIdx,tVertIdx)

	toBasis = origin

	flatEdges = layoutFace(0,initBasisInfo,foldList,mesh,toBasis,flatEdges)
	drawNet(flatEdges)

	print('Version:')
	print(sys.version )



"""FLATTEN/LAYOUT"""

def layoutFace(depth,basisInfo,foldList,mesh,toBasis,flatEdges):
	''' Recurse through faces, moving along fold edges
	'''
	transformToFlat = getTransform(basisInfo,toBasis,mesh)
	faceEdges = getFaceEdges(basisInfo[0],mesh)

	for edgeIndex in faceEdges:
		flatCoords = assignNewPntsToEdge(transformToFlat,edgeIndex,mesh)
		flatEdge = FlatEdge(edgeIndex,flatCoords)

		if (edgeIndex in foldList):
			if (not alreadyBeenPlaced(edgeIndex,flatEdges)):
				flatEdge.type  = "fold"

				flatEdges[edgeIndex].append(flatEdge)

				newBasisInfo = getNewBasisInfo(basisInfo,edgeIndex,mesh)
				newToBasis = getBasisFlat(flatCoords)

				flatEdges = layoutFace(depth+1,newBasisInfo,foldList,mesh,newToBasis,flatEdges)

		else:
			if len(flatEdges[edgeIndex])<2:
				flatEdge.type  = "cut"
				flatEdges[edgeIndex].append(flatEdge)

	return flatEdges

def alreadyBeenPlaced(testEdgeIdx,flatEdges):
	return len(flatEdges[testEdgeIdx]) > 0


def getNewBasisInfo(oldBasisInfo,testEdgeIdx, mesh):
	faceIdx,edgeIdx,tVertIdx = oldBasisInfo
	newFaceIdx = getOtherFaceIdx(testEdgeIdx,faceIdx,mesh)
	newEdgeIdx = testEdgeIdx
	newTVertIdx = mesh.TopologyEdges.GetTopologyVertices(testEdgeIdx).I #convention: useI
	return newFaceIdx,newEdgeIdx,newTVertIdx


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

"""chang name to assign edgeWeights, implicit in methods available for topoEdges"""
def assignEdgeWeights(mesh):
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

def calculateAngle(arrConnFaces,mesh):
	faceIdx0 = arrConnFaces.GetValue(0)
	faceIdx1 = arrConnFaces.GetValue(1)

	faceNorm0 = mesh.FaceNormals.Item[faceIdx0]
	faceNorm1 = mesh.FaceNormals.Item[faceIdx1]

	return rs.VectorAngle(faceNorm0,faceNorm1) #returns None on error

if __name__=="__main__":
	unwrapExampleMesh()