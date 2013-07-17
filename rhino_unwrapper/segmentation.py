from rhino_helpers import *
from layout import * 
from classes import FlatEdge


'''# this code is very similar to layoutFace() in layout.py
consider generalizing layout or something. Also maybe create a different module
that both layout and segmentation use.
'''
def segmentNet(mesh,foldList,flatEdges,flatEdgeCut,xForm):
  cutEdgeIdx = flatEdgeCut.edgeIdx

  if(cutEdgeIdx in foldList):
    #flatEdgeCut.clearAllGeom()
    flatEdgeCut.type = 'cut'
    newFlatEdge = FlatEdge(flatEdgeCut.edgeIdx,flatEdgeCut.coordinates)
    newFlatEdge.type = 'cut'
    newFlatEdge.faceIdx = getOtherFaceIdx(cutEdgeIdx,flatEdgeCut.faceIdx,mesh)
    newFlatEdge.drawLine()
    flatEdges[cutEdgeIdx].append(newFlatEdge) #copy flatEdge

    foldList.remove(cutEdgeIdx)
    segA,segB = getSegmentsFromCut(mesh,foldList,cutEdgeIdx)
    segLists = orderListsByLen(segA,segB)
    smallSeg = segLists[0]
    edgesInSeg = getEdgesInSegment(flatEdges,smallSeg)
    FlatEdge.clearEdges(edgesInSeg) # remove drawn geometry
    translateSegmentCoords(edgesInSeg,xForm)
    FlatEdge.drawEdges(edgesInSeg)

   

def translateSegmentCoords(edgesInSegment,xForm):
  for flatEdge in edgesInSegment:
    points = flatEdge.coordinates
    points[0].Transform(xForm)
    points[1].Transform(xForm)

def getEdgesInSegment(flatEdges,faceList):
  edges = []
  flatEdges = FlatEdge.getFlatList(flatEdges)
  for flatEdge in flatEdges:
    if flatEdge.faceIdx in faceList:
      edges.append(flatEdge)
  return edges





def resetFlatEdge(flatEdges,cutEdgeIdx,xForm):
  flatEdge = FlatEdge.getFlatEdgePair(flatEdges,'edgeIdx',cutEdgeIdx)[0]
  flatEdge.clearAllGeom()
  


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
  #print("faceList associated with new cut edge:" + str(faceList))
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

