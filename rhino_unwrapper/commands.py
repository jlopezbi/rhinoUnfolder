import visualization
import layout
import traversal
import weight_functions

# -RunPythonScript ResetEngine RhinoUnwrapper.Unwrap_cmd

def unwrap(mesh):
  mesh.FaceNormals.ComputeFaceNormals()
  meshGraph = traversal.buildMeshGraph(mesh, weight_functions.edgeAngle)
  foldList = traversal.getSpanningKruskal(meshGraph,mesh)
  flatEdges = layout.layoutMesh(foldList, mesh)
  visualization.drawNet(flatEdges)