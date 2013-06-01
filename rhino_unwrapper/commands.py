import visualization
import layout
import traversal

def unwrap(mesh):
  mesh.FaceNormals.ComputeFaceNormals()
  meshGraph = traversal.buildMeshGraph(mesh, graph.edgeAngle)
  foldList = traversal.getSpanningKruskal(meshGraph,mesh)
  flatEdges = layout.layoutMesh(foldList, mesh)
  visualization.drawNet(flatEdges)