import visualization
import layout
import traversal
import weight_functions
from classes import FlatEdge
from Map import Map
from Net import Net

def unwrap(mesh,faceVals,scale,userCuts,holeRadius, weightFunction=weight_functions.edgeAngle):
  '''
  input:
    mesh = mesh
    faceVals = dict of faceIdxs pointing to the buckle val for that face
    scale = float, scale of buckling for all faces
    userCuts = list of edges that are selected by the user to be cut
    holeRadius = radius of hole for joining, if fasteners are to be used
    weightFunction = function that weights the edges, highest = most likely to be cut
  '''
  
  mesh.FaceNormals.ComputeFaceNormals() 
  meshDual = traversal.buildMeshGraph(mesh, userCuts, weightFunction)
  foldList = traversal.getSpanningKruskal(meshDual,mesh)
  cutList = traversal.getCutList(mesh,foldList)
  net,dataMap = layout.layoutMesh(foldList, mesh,holeRadius,userCuts)

  
  '''VISUALZE UNFOLDING ON MESH'''
  #visualization.displayMeshEdges(mesh,(0,255,0,255),userCuts,"userCuts")
  visualization.displayMeshEdges(mesh,(0,255,0,0),cutList,"cuts")
  #visualization.displayMeshEdges(mesh,(0,0,255,0),foldList,"foldEdges")

  '''DRAW NET'''
  netGroupName = "net1"
  net.drawEdges(netGroupName,faceVals,scale)
  #net.drawHoles(netGroupName)
  #net.drawFaces(netGroupName)

  #FlatEdge.drawEdges(flatVerts,flatEdgesSimple,netGroupName)
  #FlatEdge.drawTabs(flatVerts,flatEdgesSimple,netGroupName,)
  
  return dataMap,net,foldList  

