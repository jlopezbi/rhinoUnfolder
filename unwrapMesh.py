import rhinoscriptsyntax as rs
import random, math, time
import Rhino
import scriptcontext
import sys
import itertools
import System.Guid

import layout
reload(layout)
from layout import *

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



if __name__=="__main__":
	unwrapExampleMesh()