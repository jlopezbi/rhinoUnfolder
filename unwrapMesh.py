import rhinoscriptsyntax as rs
import random, math, time
import Rhino
import scriptcontext
import sys
import itertools
import System.Guid

import graph
reload(graph)
from graph import *

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


if __name__=="__main__":
	unwrapExampleMesh()