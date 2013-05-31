import matTrussToMesh
import visualization
import layout
import graph

def unwrap(mesh):
  faces,edge_weights,thetaMax = graph.assignEdgeWeights(mesh)
  foldList = graph.getSpanningKruskal(faces,edge_weights,mesh)
  flatEdges = layout.layoutMesh(foldList, mesh)
  visualization.drawNet(flatEdges)

if __name__=="__main__":
  mesh = matTrussToMesh.loadExampleMesh()
  unwrap(mesh)