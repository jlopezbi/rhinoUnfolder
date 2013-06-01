import matTrussToMesh
import visualization
import layout
import graph
import Rhino

def unwrap(mesh):
  faces,edge_weights,thetaMax = graph.assignEdgeWeights(mesh)
  foldList = graph.getSpanningKruskal(faces,edge_weights,mesh)
  flatEdges = layout.layoutMesh(foldList, mesh)
  visualization.drawNet(flatEdges)