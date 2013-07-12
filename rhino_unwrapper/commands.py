import visualization
import layout
import traversal
import weight_functions

def unwrap(mesh, userCuts, weightFunction=weight_functions.edgeAngle):
  mesh.FaceNormals.ComputeFaceNormals() 
  meshDual = traversal.buildMeshGraph(mesh, userCuts, weightFunction)
  foldList = traversal.getSpanningKruskal(meshDual,mesh)
  cutList = traversal.getCutList(mesh,foldList)
  flatEdges = layout.layoutMesh(foldList, mesh)
  
  netGroupName = visualization.drawNet(flatEdges)

  visualization.displayMeshEdges(mesh,(0,255,0,255),userCuts,"userCuts")
  visualization.displayMeshEdges(mesh,(0,255,0,0),cutList,"algoCuts")
  return flatEdges	
	
def segmentNet(mesh,foldList,flatEdges,cutEdgeIdx):
	foldList.remove(cutEdgeIdx)
	