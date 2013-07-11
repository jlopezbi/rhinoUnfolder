import visualization
import layout
import traversal
import weight_functions

def unwrap(mesh, userCuts, weightFunction=weight_functions.edgeAngle):
  mesh.FaceNormals.ComputeFaceNormals() 
  meshDual = traversal.buildMeshGraph(mesh, userCuts, weightFunction)
  foldList = traversal.getSpanningKruskal(meshDual,mesh)
  flatEdges = layout.layoutMesh(foldList, mesh)
  visualization.drawNet(flatEdges)
  visualization.displayMeshEdges(mesh,(0,255,0,255),userCuts)
  visualization.displayMeshCutEdges(mesh,foldList)

