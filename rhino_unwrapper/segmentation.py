import Rhino
import rhinoscriptsyntax as rs
from rhino_helpers import *
from layout import * 
import scriptcontext

'''# this code is very similar to layoutFace() in layout.py
consider generalizing layout or something. Also maybe create a different module
that both layout and segmentation use.
'''
def deleteSmallerSegment(flatEdges,cutEdgeIdx,segA,segB):
  if len(segA)<=len(segB):
    segment = segA
  else:
    segment = segB

  for flatEdgePair in flatEdges:
    for flatEdge in flatEdgePair:
      if flatEdge.faceIdx in segment and flatEdge.edgeIdx != cutEdgeIdx:
        scriptcontext.doc.Objects.Delete(flatEdge.geom,True)
        flatEdge.geom = None
  return segment

def getSegmentsFromCut(mesh,foldList,cutEdgeIdx):
  faceList = getFacesForEdge(mesh,cutEdgeIdx)
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

    if(edgeIdx in foldList):
      newFaceIdx = getOtherFaceIdx(edgeIdx,faceIdx,mesh)
      segment = createSegment(mesh,newFaceIdx,foldList,segment)
    else:
      return segment

