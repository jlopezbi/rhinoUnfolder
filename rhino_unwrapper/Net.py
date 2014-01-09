from segmentation import segmentIsland
from rhino_helpers import createGroup,getEdgesForVert
from classes import FlatVert,FlatEdge
import Rhino
import rhinoscriptsyntax as rs
import math

class Net():
  def __init__(self,mesh,holeRadius,tabAngle,buckleScale,buckleVals,drawTabs,drawFaceHoles):
    self.holeRadius = holeRadius #holes used for fastening joinery
    self.tabAngle = tabAngle #innner tab angle for all tabs in net
    self.buckleScale = buckleScale #scale for the buckling offset
    self.buckleVals = buckleVals #dict mapping faceIdx to buckleVal
    self.drawTabs = drawTabs #boolean
    self.drawFaceHoles = drawFaceHoles #boolean face holes == mouth etc.

    self.flatVerts = []
    self.flatEdges = []
    self.flatFaces = [None]*mesh.Faces.Count
    self.angleThresh = math.radians(3.3)
    self.mesh = mesh

    #self.groups,self.leaders = segmentIsland(self.flatFaces,[])
    
  def addEdge(self,flatEdge,flatFace):
    '''
    adds a flatEdge to the flatEdges array
    input:
      flatEdge = the new flatEdge to add (instance of FlatEdge class)
      flatFace = the flatFace which will have this edge (instance of FlatFace class)
    '''
    flatFace.flatEdges.append(flatEdge) #each flatFace stores an array of its flatEdges
    self.flatEdges.append(flatEdge)
    return len(self.flatEdges)-1
  
  def addVert(self,flatVert):
    self.flatVerts.append(flatVert)
    return len(self.flatVerts)-1

  '''SEGMENTATION'''
  def findInitalSegments(self):
    group,leader = segmentIsland(self.flatFaces,[])
    self.groups = group
    self.leaders = leader

  def findSegment(self,flatEdgeCut,face):
    assert(flatEdgeCut.type == 'fold')
    island = self.getGroupForMember(face)
    self.removeFaceConnection(flatEdgeCut)
    group,leader = segmentIsland(self.flatFaces,island)
    self.updateIslands(group,leader,face)
    return group[leader[face]]

  def copyAndReasign(self,mesh,dataMap,flatEdgeCut,edgeIdx,segment,segmentFace):
    '''
    input:
      mesh = mesh
      dataMap = class which maps mesh elements to net elements
      flatEdgeCut = the flatEdge whcih has been selected by the user to segment net
      edgeIdx = the index of the flatEdge (TODO: get this from the flatEdgeCut?)
      segment = the segment that is to be translated
      segmentFace = the segmentFace on the segment side of the selected edge
    '''
    flatEdgeCut.type = 'cut'
    nonSegmentFace = flatEdgeCut.resetFromFace(segmentFace)
    changedVertPairs = self.makeNewNetVerts(dataMap,flatEdgeCut)
    newNetEdgeIdx,newFlatEdge = self._makeNewEdge(dataMap,changedVertPairs,flatEdgeCut.edgeIdx,edgeIdx,segmentFace)
    newFlatEdge.tabFaceCenter = self.flatFaces[nonSegmentFace].getCenterPoint(self.flatVerts)
    self.flatFaces[segmentFace].resetFlatEdges(newFlatEdge)
    flatEdgeCut.pair = newNetEdgeIdx
    flatEdgeCut.tabFaceCenter = self.flatFaces[segmentFace].getCenterPoint(self.flatVerts)
    flatEdgeCut.drawNetEdge(self)
    self.resetSegment(mesh,dataMap,changedVertPairs,segment)

  def translateSegment(self,segment,xForm):
    #TODO: make a more efficent version of this, would be easier if half-edge or
    #winged edge mesh. H-E: could traverse edges recursively, first going to sibling h-edge
    #stopping when the edge points to no other edge(naked),or to a face not in the segment,or
    #if the h-edge is part of the user-selected edge to be cut

    translatedEdges = []
    movedNetVerts = []
    for netEdge in self.flatEdges:
      if netEdge.fromFace in segment:
        translatedEdges.append(netEdge)
        netEdge.translateNetVerts(movedNetVerts,self.flatVerts,xForm)
        netEdge.translateTabFaceCenter(xForm)
    return translatedEdges

  def removeFaceConnection(self,flatEdgeCut):
    faceA = flatEdgeCut.fromFace
    faceB = flatEdgeCut.toFace
    netFaceA = self.flatFaces[faceA]
    netFaceB = self.flatFaces[faceB]
    if netFaceB.fromFace==faceA:
      netFaceB.fromFace = None
    elif netFaceA.fromFace==faceB:
      netFaceA.fromFace = None

  def _makeNewEdge(self,dataMap,changedVertPairs,meshEdge,idx,face):
    newVertI = changedVertPairs[0][0]
    newVertJ = changedVertPairs[1][0]
    newFlatEdge = FlatEdge(meshEdge,newVertI,newVertJ)
    newFlatEdge.fromFace = face
    newFlatEdge.type = 'cut'
    #newFlatEdge.hasTab = True
    newFlatEdge.pair = idx
    #newFlatEdge.hasTab = True
    #TODO: need to set tab angles or something. NOTE: .fromFace and .toFace of flatEdge referes to a MESH face,
    #wait silly: mesh faces and net faces are the same!!
    netEdge = self.addEdge(newFlatEdge,self.flatFaces[face])
    dataMap.updateEdgeMap(meshEdge,netEdge)
    return netEdge,newFlatEdge

  def makeNewNetVerts(self,dataMap,flatEdgeCut):
    oldNetI,oldNetJ = flatEdgeCut.getNetVerts()
    flatI,flatJ = flatEdgeCut.getFlatVerts(self.flatVerts)
    pointI = Rhino.Geometry.Point3d(flatI.point) #important copy vert
    pointJ = Rhino.Geometry.Point3d(flatJ.point)
    newI = FlatVert(flatI.tVertIdx,pointI)
    newJ = FlatVert(flatJ.tVertIdx,pointJ)
    newNetI = self.addVert(newI)
    newNetJ = self.addVert(newJ)
    dataMap.updateVertMap(flatI.tVertIdx,newNetI)
    dataMap.updateVertMap(flatJ.tVertIdx,newNetJ)
    return [(newNetI,oldNetI),(newNetJ,oldNetJ)]

  def resetSegment(self,mesh,dataMap,changedVertPairs,segment):
    self.resetFaces(changedVertPairs,segment)
    self.resetEdges(mesh,dataMap,changedVertPairs,segment)

  def resetFaces(self,changedVertPairs,segment):
    '''
    reset the faces to contain the newley added flatVertices
    '''
    #if better data structure: REPLACE: this is slow hack
    newVertI,oldVertI = changedVertPairs[0]
    newVertJ,oldVertJ = changedVertPairs[1]
    for face in segment:
      verts = self.flatFaces[face].vertices
      if oldVertI in verts:
        index = verts.index(oldVertI)
        verts.insert(index,newVertI) #does order matter? yes
        verts.pop(index+1)
      if oldVertJ in verts:
        index = verts.index(oldVertJ)
        verts.insert(index,newVertJ) #does order matter? yes
        verts.pop(index+1)

  def resetEdges(self,mesh,dataMap,changedVertPairs,segment):
    '''
    reset all edges touching the newely added vertices
    '''
    #REPLACE: if using he-mesh then this will be unnecessary
    for pair in changedVertPairs:
      newVert,oldVert = pair
      tVert = self.flatVerts[newVert].tVertIdx
      edges = getEdgesForVert(mesh,tVert) #in original mesh,eventually use he-mesh
      for edge in edges:
        netEdges = dataMap.getNetEdges(edge)
        for netEdge in netEdges:
          flatEdge = self.getFlatEdge(netEdge)
          netPair = flatEdge.getNetVerts()
          if oldVert in netPair and flatEdge.fromFace in segment:
            #assert(flatEdge.fromFace in segment), "flatEdge not in segment"
            flatEdge.reset(oldVert,newVert)

  def getGroupForMember(self,member):
    if member not in self.leaders.keys():
      print "face not in leaders: ",
      print member
      return
    leader = self.leaders[member]
    return self.groups[leader]

  def updateIslands(self,newGroups,newLeaders,face):
    #get rid of old island
    leader = self.leaders[face]
    del self.groups[leader]

    for group in newGroups.items():
      self.groups[group[0]] = group[1]
    for leader in newLeaders.items():
      self.leaders[leader[0]] = leader[1]


  '''SELECTION'''
  def getFlatEdgeForLine(self,value):
    #assert guid?
    for i,flatEdge in enumerate(self.flatEdges):
      if flatEdge.line_id == value:
        return flatEdge,i
    return
    
  def getFlatEdge(self,netEdge):
    return self.flatEdges[netEdge]
    
    
  '''DRAWING'''
  def redrawSegment(self,translatedEdges):
    group = rs.AddGroup()
    geom = []
    for netEdge in translatedEdges:
      netEdge.clearAllGeom()
      geom.append(netEdge.drawNetEdge(self))
    grouped =  rs.AddObjectsToGroup(geom,group)
    if grouped==None: 
      print "failed to make segment group"
    else:
      print "made segment group of" + str(grouped) +" elements"

  def drawEdges(self,netGroupName):
    '''
    draw all edge geometry for the net
    input:
      netGroupName = name for the group
      buckleVals = dictionary mapping faceIdx to buckling val (not yet adjusted for edgeLen)
    '''
    collection = []
    for netEdge in self.flatEdges:

      #if netEdge.type=='cut':
        #netEdge.drawHoles(self,connectorDist,safetyRadius,holeRadius)
      fromFace = netEdge.fromFace
      buckleVal = self.buckleVals[fromFace]
      subCollection = netEdge.drawNetEdge(self)
      for item in subCollection:
        collection.append(item)
    createGroup(netGroupName,collection)

  def drawFaces(self,netGroupName):
    collection = []
    for face in self.flatFaces:
      collection.append(face.draw(self.flatVerts))
    createGroup(netGroupName,collection)


