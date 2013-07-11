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
  visualization.displayMeshCutEdges(mesh,foldList)
