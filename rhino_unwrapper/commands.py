import visualization
import layout
import graph

def unwrap(mesh):
  mesh.FaceNormals.ComputeFaceNormals()
  faces,edge_weights = graph.buildMeshGraph(mesh, graph.edgeAngle)
  foldList = graph.getSpanningKruskal(faces,edge_weights,mesh)
  flatEdges = layout.layoutMesh(foldList, mesh)
  visualization.drawNet(flatEdges)