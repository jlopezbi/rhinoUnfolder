import visualization
import layout
import traversal
import weight_functions
from classes import FlatEdge
from Map import Map
from Net import Net

def unwrap(mesh, userCuts,holeRadius, weightFunction=weight_functions.edgeAngle):
  mesh.FaceNormals.ComputeFaceNormals() 
  meshDual = traversal.buildMeshGraph(mesh, userCuts, weightFunction)
  foldList = traversal.getSpanningKruskal(meshDual,mesh)
  cutList = traversal.getCutList(mesh,foldList)
  net,dataMap = layout.layoutMesh(foldList, mesh,holeRadius)

  

  #visualization.displayMeshEdges(mesh,(0,255,0,255),userCuts,"userCuts")
  visualization.displayMeshEdges(mesh,(0,255,0,0),cutList,"cuts")
  #visualization.displayMeshEdges(mesh,(0,0,255,0),foldList,"foldEdges")

  netGroupName = "net1"
  net.drawEdges(netGroupName)
  #net.drawHoles(netGroupName)
  #net.drawFaces(netGroupName)

  #FlatEdge.drawEdges(flatVerts,flatEdgesSimple,netGroupName)
  #FlatEdge.drawTabs(flatVerts,flatEdgesSimple,netGroupName,)
  
  return dataMap,net,foldList  

