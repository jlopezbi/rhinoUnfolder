import visualization
import layout
import traversal

# -RunPythonScript ResetEngine RhinoUnwrapper.Unwrap_cmd

def unwrap(mesh):
  mesh.FaceNormals.ComputeFaceNormals()
  meshGraph = traversal.buildMeshGraph(mesh, traversal.edgeAngle)
  foldList = traversal.getSpanningKruskal(meshGraph,mesh)
  flatEdges = layout.layoutMesh(foldList, mesh)
  visualization.drawNet(flatEdges)