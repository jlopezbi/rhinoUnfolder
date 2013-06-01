import visualization
import layout
import traversal
import weight_functions

def unwrap(mesh, weightFunction=weight_functions.edgeAngle):
  mesh.FaceNormals.ComputeFaceNormals() 
  meshGraph = traversal.buildMeshGraph(mesh, weightFunction)
  foldList = traversal.getSpanningKruskal(meshGraph,mesh)
  flatEdges = layout.layoutMesh(foldList, mesh)
  visualization.drawNet(flatEdges)
  visualization.displayMeshCutEdges(mesh,foldList)
