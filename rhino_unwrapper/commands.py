import visualization
import layout
import traversal
import weight_functions
from classes import FlatEdge

def unwrap(mesh, userCuts, weightFunction=weight_functions.edgeAngle):
  mesh.FaceNormals.ComputeFaceNormals() 
  meshDual = traversal.buildMeshGraph(mesh, userCuts, weightFunction)
  foldList = traversal.getSpanningKruskal(meshDual,mesh)
  cutList = traversal.getCutList(mesh,foldList)
  flatVerts,flatEdges,flatFaces = layout.layoutMesh(foldList, mesh)
  

  #visualization.displayMeshEdges(mesh,(0,255,0,255),userCuts,"userCuts")
  visualization.displayMeshEdges(mesh,(0,255,0,0),cutList,"algoCuts")
  #visualization.displayMeshEdges(mesh,(0,0,255,0),foldList,"foldEdges")

  netGroupName = "net0"
  flatEdgesSimple = FlatEdge.getFlatList(flatEdges)
  FlatEdge.drawEdges(flatVerts,flatEdgesSimple,netGroupName)
  FlatEdge.drawTabs(flatEdgesSimple,netGroupName,flatVerts)
  
  return flatVerts,flatEdges,flatFaces,foldList  

