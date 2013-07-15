import visualization
import layout
import traversal
import weight_functions
import segmentation as segm

def unwrap(mesh, userCuts, weightFunction=weight_functions.edgeAngle):
  mesh.FaceNormals.ComputeFaceNormals() 
  meshDual = traversal.buildMeshGraph(mesh, userCuts, weightFunction)
  foldList = traversal.getSpanningKruskal(meshDual,mesh)
  cutList = traversal.getCutList(mesh,foldList)
  flatEdges = layout.layoutMesh(foldList, mesh)
  
  netGroupName = visualization.drawNet(flatEdges)

  visualization.displayMeshEdges(mesh,(0,255,0,255),userCuts,"userCuts")
  visualization.displayMeshEdges(mesh,(0,255,0,0),cutList,"algoCuts")
  visualization.displayMeshEdges(mesh,(0,0,255,0),foldList,"foldEdges")
  return flatEdges,foldList  
  
def segmentNet(mesh,foldList,flatEdges,cutEdgeIdx):
  if(cutEdgeIdx in foldList):
    foldList.remove(cutEdgeIdx)
    segA,segB = segm.getSegmentsFromCut(mesh,foldList,cutEdgeIdx)
    print("segA")
    print(segA)
    print("segB")
    print(segB)
    smallSegment = segm.deleteSmallerSegment(flatEdges,cutEdgeIdx,segA,segB)
