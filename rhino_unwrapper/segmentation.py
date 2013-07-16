from rhino_helpers import *
from layout import * 


'''# this code is very similar to layoutFace() in layout.py
consider generalizing layout or something. Also maybe create a different module
that both layout and segmentation use.
'''
def segmentNet(mesh,foldList,flatEdges,flatEdgeCut,xForm):
  cutEdgeIdx = flatEdgeCut.edgeIdx
  if(cutEdgeIdx in foldList):
    foldList.remove(cutEdgeIdx)
    segA,segB = segm.getSegmentsFromCut(mesh,foldList,cutEdgeIdx)
    segLists = segm.orderListsByLen(segA,segB)
    smallSeg = segLists[0]
    #smallSegment = segm.deleteSmallerSegment(flatEdges,cutEdgeIdx,segA,segB)
    segm.translateSmallerSegment(flatEdges,cutEdgeIdx,smallSeg,xForm)

def translateSmallerSegment(flatEdges,cutEdgeIdx,smallSeg,xForm):
  #something in here appears to be rather slow :(
  segmentEdges = []
  for flatEdgePair in flatEdges:
    for flatEdge in flatEdgePair:
      if flatEdge.faceIdx in smallSeg and flatEdge.edgeIdx != cutEdgeIdx:
        #scriptcontext.doc.Objects.Delete(flatEdge.geom,True)
        #scriptcontext.doc.Objects.Replace(flatEdges.geom,)
        segmentEdges.append(flatEdge.line_id)
        if len(flatEdge.geom)>0:
          for guid in flatEdge.geom:
            segmentEdges.append(guid)
  rs.TransformObjects(segmentEdges,xForm,False) 


def orderListsByLen(listA,listB):
  '''
  return list where first element is the shorter list. or listA if equal
  '''
  smallList = listA
  bigList = listB
  if len(listA)>len(listB):
    bigList = listA
    smallList = listB
  return [smallList,bigList]


def getSegmentsFromCut(mesh,foldList,cutEdgeIdx):
  faceList = getFacesForEdge(mesh,cutEdgeIdx)
  print("faceList associated with new cut edge:" + str(faceList))
  if(len(faceList)==1):
    print("selected a naked edge!")
    return
  elif(len(faceList)>1):
    segA = set()
    segB = set()

    segA = createSegment(mesh,faceList[0],foldList,segA)
    segB = createSegment(mesh,faceList[1],foldList,segB)

  return segA,segB

def createSegment(mesh,faceIdx,foldList,segment):
  '''
  recurse through mesh, starting at faceIdx, adding each face to segment set
  '''
  segment.add(faceIdx) # this is a set
  edgesForFace = getFaceEdges(faceIdx,mesh)

  for edgeIdx in edgesForFace:
    newFaceIdx = getOtherFaceIdx(edgeIdx,faceIdx,mesh)
    if(edgeIdx in foldList):
      if newFaceIdx not in segment:
        segment = createSegment(mesh,newFaceIdx,foldList,segment)
    # else:
    #   return segment
  return segment

