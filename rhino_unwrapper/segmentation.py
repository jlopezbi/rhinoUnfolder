from rhino_helpers import *
from layout import * 
from classes import FlatEdge,FlatVert

'''# this code is very similar to layoutFace() in layout.py
consider generalizing layout or something. Also maybe create a different module
that both layout and segmentation use.
'''
def segmentNet(mesh,foldList,flatVerts,flatEdges,flatFaces,flatEdgeCut,xForm):
  cutEdgeIdx = flatEdgeCut.edgeIdx

  if(cutEdgeIdx in foldList):
    flatEdgeCut.clearAllGeom()
    flatEdgeCut.type = 'cut'
    flatEdgeCut.drawLine(flatVerts)

    newFace = getOtherFaceIdx(cutEdgeIdx,flatEdgeCut.faceIdx,mesh)
    newSpecs = copyFlatVerts(flatEdgeCut,flatVerts)
    

    newFlatEdge = FlatEdge(flatEdgeCut.edgeIdx,flatEdgeCut.tVertIdxs,newSpecs)
    newFlatEdge.type = 'cut'
    newFlatEdge.faceIdx = newFace
    newFlatEdge.drawLine(flatVerts)
    flatEdges[cutEdgeIdx].append(newFlatEdge) #copy flatEdge

    foldList.remove(cutEdgeIdx)
    segA,segB = getSegmentsFromCut(mesh,foldList,cutEdgeIdx)
    segLists = orderListsByLen(segA,segB)
    smallSeg = segLists[0]
    edgesInSeg = getElementsInSegment(flatEdges,smallSeg)
    #vertsInSeg = getElementsInSegment(flatVerts,smallSeg)
    vertsInSeg = getFlatVertsInSegment(flatVerts,flatFaces,smallSeg)
    FlatEdge.clearEdges(edgesInSeg) # remove drawn geometry
    translateSegmentVerts(vertsInSeg,xForm)
    FlatEdge.drawEdges(flatVerts,edgesInSeg,'seg1')

def copyFlatVerts(flatEdge,flatVerts):
  flatI,flatJ = flatEdge.getFlatVerts(flatVerts)
  I = flatEdge.tVertIdxs[0]
  J = flatEdge.tVertIdxs[1]

  newFlatI = FlatVert(I,flatI.point)
  newFlatJ = FlatVert(J,flatJ.point)
 
  flatVerts[I].append(newFlatI) #make copies
  flatVerts[J].append(newFlatJ)

  specI = len(flatVerts[I])-1 #make specs for new edge
  specJ = len(flatVerts[J])-1
  newSpecs = {I:specI,J:specJ}

  return newSpecs



def translateSegmentVerts(tVerts,xForm):
  for flatVert in tVerts:
    point = flatVert.point
    point.Transform(xForm)


def translateSegmentCoords(edgesInSegment,xForm):
  getAssociatedFlatVerts(edgesInSegment,flat)
  for flatEdge in edgesInSegment:
    points = flatEdge.coordinates
    points[0].Transform(xForm)
    points[1].Transform(xForm)

def getFlatVertsInSegment(flatVerts,flatFaces,segment):
  collection = set()
  for face in segment:
    flatFace = flatFaces[face]
    verts = flatFace.getFlatVerts(flatVerts)
    for vert in verts:
      collection.add(vert)
  return list(collection)

def getElementsInSegment(elements,faceList):
  collection = []
  allElements = getFlatList(elements)
  for element in allElements:
    if element.faceIdx in faceList:
      collection.append(element)
  return collection



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

