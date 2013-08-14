from segmentation import segmentIsland
from rhino_helpers import createGroup,getEdgesForVert
from classes import FlatVert
import Rhino

class Net():
  def __init__(self,mesh):
    self.flatVerts = []
    self.flatEdges = []
    self.flatFaces = [None]*mesh.Faces.Count

    #self.groups,self.leaders = segmentIsland(self.flatFaces,[])
    
  def addEdge(self,flatEdge):
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

  def copyAndReasign(self,mesh,dataMap,flatEdgeCut,segment):
    changedVertPairs = self.makeNewNetVerts(dataMap,flatEdgeCut)
    self.resetSegment(mesh,dataMap,changedVertPairs,segment)

  def translateSegment(self,segment,xForm):
    #TODO: make a more efficent version of this, would be easier if half-edge or
    #winged edge mesh. H-E: could traverse edges recursively, first going to sibling h-edge
    #stopping when the edge points to no other edge(naked),or to a face not in the segment,or
    #if the h-edge is part of the user-selected edge to be cut
    
    #collection = []
    movedNetVerts = []
    for netEdge in self.flatEdges:
      if netEdge.fromFace in segment:
        #collection.append[netEdge]
        netEdge.translateGeom(movedNetVerts,self.flatVerts,xForm)
        netEdge.drawEdgeLine(self.flatVerts)
    #return collection

  def removeFaceConnection(self,flatEdgeCut):
    faceA = flatEdgeCut.fromFace
    faceB = flatEdgeCut.toFace
    netFaceA = self.flatFaces[faceA]
    netFaceB = self.flatFaces[faceB]
    if netFaceB.fromFace==faceA:
      netFaceB.fromFace = None
    elif netFaceA.fromFace==faceB:
      netFaceA.fromFace = None

  

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
    #REPLACE: this is slow hack
    newVertI,oldVertI = changedVertPairs[0]
    newVertJ,oldVertJ = changedVertPairs[1]
    for face in segment:
      verts = self.flatFaces[face].vertices
      if oldVertI in verts:
        verts.remove(oldVertI)
        verts.append(newVertI) #does order matter?
      if oldVertJ in verts:
        verts.remove(oldVertJ)
        verts.append(newVertJ) #does order matter?


  def resetEdges(self,mesh,dataMap,changedVertPairs,segment):
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
    for flatEdge in self.flatEdges:
      if flatEdge.line_id == value:
        return flatEdge
    return
    
  def getFlatEdge(self,netEdge):
    return self.flatEdges[netEdge]
    
    

  '''DRAWING'''
  def drawEdges(self,netGroupName):
    collection = []
    for netEdge in self.flatEdges:
      collection.append(netEdge.drawEdgeLine(self.flatVerts))
    createGroup(netGroupName,collection)
