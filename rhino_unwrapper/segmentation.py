from rhino_helpers import *
from layout import * 
from classes import FlatEdge,FlatVert
from System.Diagnostics import Stopwatch
from UnionFind import UnionFind


def segmentNet(mesh,foldList,dataMap,net,flatEdgeCut,face,xForm):

  cutEdgeIdx = flatEdgeCut.edgeIdx

  if(cutEdgeIdx in foldList):

  
    foldList.remove(cutEdgeIdx)

    smallSeg,bigSeg = findSegments(mesh,foldList,cutEdgeIdx,net.flatFaces)
    
    resetEdge(mesh,flatEdgeCut,foldList,net.flatVerts,smallSeg)    
    newI,newJ = copyFlatVerts(dataMap,flatEdgeCut,net)     

    newFlatEdge = createNewEdge(mesh,dataMap,net,flatEdgeCut,newI,newJ,face)
    newFlatEdge.drawEdgeLine(net.flatVerts)  
    resetEdges(mesh,net,newFlatEdge,newSpecs,smallSeg)
    resetFaces(mesh,net.flatFaces,newFlatEdge,smallSeg,newSpecs) 
  
   
    edgesInSeg = getEdgesInSegment(net.flatEdges,newFlatEdge,smallSeg)
    vertsInSeg = getFlatVertsInSegment(net.flatVerts,net.flatFaces,smallSeg)  
    translateLines(edgesInSeg,xForm)
    #FlatEdge.clearEdges(edgesInSeg) # remove drawn geometry
    translateSegmentVerts(vertsInSeg,xForm,flatVerts)
    
  

    
    #FlatEdge.translateGeom(edgesInSeg,xForm)
    #FlatEdge.drawEdges(flatVerts,edgesInSeg,'seg1')
    #FlatEdge.drawTabs(flatVerts,edgesInSeg,'seg1')    
    flatEdgeCut.clearAllGeom()
    flatEdgeCut.drawEdgeLine(flatVerts)

'''New Faster methods'''

def findSegments(mesh,foldList,cutEdgeIdx,flatFaces):

  faceA,faceB = removePointer(mesh,cutEdgeIdx,flatFaces)
  group,leader = segmentIsland(flatFaces,[])
  segA = group[group.keys()[0]]
  segB = group[group.keys()[1]]
  
  segLists = orderListsByLen(segA,segB)

  
  return segA,segB

def segmentIsland(flatFaces,island):
  sets = UnionFind(True)
  if len(island)==0:
    island = range(len(flatFaces))
  for face in island:
    if face not in sets.leader.keys():
      sets.makeSet([face])
    neighbor = flatFaces[face].fromFace  
    if neighbor != None:
      if neighbor not in sets.leader.keys():
        sets.makeSet([neighbor])
      sets.union(face,neighbor)
  return sets.group, sets.leader

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

def removePointer(mesh,cutEdgeIdx,flatFaces):
  A,B = getFacesForEdge(mesh,cutEdgeIdx)
  if A == None or B==None:
    return

  if flatFaces[A].fromFace == B:
    flatFaces[A].fromFace = None
  elif flatFaces[B].fromFace == A:
    flatFaces[B].fromFace = None
  else:
    print "faces %d and %d, associated with edge %d were not connected" %(A,B,cutEdgeIdx)
    return
  return (A,B)

    

def translateLines(edgesInSeg,xForm):
  for flatEdge in edgesInSeg:
    flatEdge.translateEdgeLine(xForm)

def modifyEdges(mesh,flatEdges,flatFaces,flatEdgeCut,newFlatEdge,newSpecs):
  modifiedEdges = getModEdges(mesh,flatEdges,flatFaces,newFlatEdge,newSpecs)
  for flatEdge in modifiedEdges:
    flatEdge.update(newSpecs)

def resetEdges(mesh,net,dataMap,newFlatEdge,netVertI,netVertJ,segment):
  netVerts = [newFlatEdge.I,newFlatEdge,J]
  for netVert in netVerts:
    tVert = netVert.tVertIdx
    edges = getEdgesForVert(mesh,tVert) #in original mesh
    for edge in edges:
      potEdges = dataMap.getNetEdges(edge)
      for netEdge in potEdges:
        if netEdge.fromFace in segment:
          netEdge.I = netVertI
          netEdge.J = netVertJ

def resetEdge(mesh,flatEdgeCut,foldList,flatVerts,moveSeg):
  cutEdgeIdx = flatEdgeCut.edgeIdx
  flatEdgeCut.type = 'cut'
  if flatEdgeCut.fromFace in moveSeg:
    flatEdgeCut.fromFace = flatEdgeCut.toFace
  elif flatEdgeCut.toFace in moveSeg:
    flatEdgeCut.toFace = flatEdgeCut.fromFace

def resetFaces(mesh,flatFaces,newFlatEdge,smallSeg,newSpecs):
  tVerts = newFlatEdge.tVertIdxs
  for vert in tVerts:
    faces = getFacesforVert(mesh,vert)
    for face in faces:
      if face in smallSeg:
        flatFaces[face].reAssignVerts(newSpecs)

def createNewEdge(mesh,dataMap,net,flatEdgeCut,newI,newJ,face):
  cutEdgeIdx = flatEdgeCut.edgeIdx
  newFlatEdge = FlatEdge(cutEdgeIdx,newI,newJ)
  newFlatEdge.type = 'cut'
  #must have reset edge for following line to work
  newFlatEdge.fromFace = face
  netEdge = net.addEdge(newFlatEdge)
  dataMap.updateEdgeMap(cutEdgeIdx,netEdge)
  return newFlatEdge

def copyFlatVerts(dataMap,flatEdge,net):
  flatVerts = net.flatVerts
  flatI,flatJ = flatEdge.getFlatVerts(flatVerts)
  I = flatI.tVertIdx
  J = flatJ.tVertIdx
  pointI = Rhino.Geometry.Point3d(flatI.point) #important copy vert
  pointJ = Rhino.Geometry.Point3d(flatJ.point)

  newFlatI = FlatVert(I,pointI)
  newFlatJ = FlatVert(J,pointJ)
 
  netVertI = net.addVert(newFlatI) #make copies
  netVertJ = net.addVert(newFlatJ)
  dataMap.updateVertMap(I,netVertI)
  dataMap.updateVertMap(J,netVertJ)
  return (netVertI,netVertJ)


def translateSegmentVerts(verts,xForm,flatVerts):
  for flatVertSpec in verts:
    row = flatVertSpec[0]
    col = flatVertSpec[1]
    flatVerts[row][col].point.Transform(xForm)

def translateSegmentCoords(edgesInSegment,xForm):
  getAssociatedFlatVerts(edgesInSegment,flat)
  for flatEdge in edgesInSegment:
    points = flatEdge.coordinates
    points[0].Transform(xForm)
    points[1].Transform(xForm)

def getFlatVertsInSegment(flatVerts,flatFaces,segment):
  collection = set() #use set to avoid duplicates
  for face in segment:
    flatFace = flatFaces[face]
    verts = flatFace.vertices.items() #list of tuples (key,value)
    for vert in verts:
      collection.add(vert)
  return list(collection)

def getEdgesInSegment(flatEdges,faceList):
  collection = []
  allElements = getFlatList(flatEdges)
  for element in allElements:
    if element.faceIdx in faceList:
      collection.append(element)
  return collection
  

'''Old Rescursive methods (slow)'''
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

  return list(segA),list(segB)

def createSegment(mesh,faceIdx,foldList,segment):
  '''
  recurse through mesh, starting at faceIdx, adding each face to segment set
  '''
  segment.add(faceIdx) # this is a set
  edgesForFace = getFaceEdges(faceIdx,mesh)

  for edgeIdx in edgesForFace:
    if(edgeIdx in foldList):
      newFaceIdx = getOtherFaceIdx(edgeIdx,faceIdx,mesh)
      if newFaceIdx not in segment:
        segment = createSegment(mesh,newFaceIdx,foldList,segment)
    
  return segment

def somethingElse(mesh,groups,leaders,flatFaces,flatEdgeCut):
  '''
  input:
    mesh = Rhion.Geometry.Mesh() instance
    groups = dictionary with leader faces pointing to set of faceIdxs
    leaders = dictionary faceIdx points to leader face for the set its in
    flatFaces = list of FlatFace objects
    flatEdgeCut = flatEdge that was selected to be a new cut
  returns fields .group and .leader from UnionFind class
  '''
  
  if groups!=None and leaders!=None and flatEdgeCut!=None:
    faceA,faceB = removePointer(mesh,flatEdgeCut.edgeIdx,flatFaces)
    leaderA = leaders[faceA]
    leaderB = leaders[faceB]
    faces = groups.pop[leaderA]
  else:
    leaderA = None
    leaderB = None
    faces = range(mesh.Faces.Count)

  if leaderA==leaderB:
    island = UnionFind(True)

    for face in faces:
      islandMembers = island.leader.keys()
      if face not in islandMembers:
        island.makeSet([face])
      neighbor = flatFaces[face].fromFace  
      if neighbor != None and neighbor not in islandMembers:
          island.makeSet([neighbor])
      island.union(face,neighbor)
    return island.group, island.leader
  else:
    print "faces A,B [with flatEdge %d] in seperate islands" %flatEdgeCut.edgeIdx
    return









