from segmentation import segmentIsland
from rhino_helpers import createGroup
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
    group,leader = segmentIsland(self.flatFaces,island)
    self.updateIslands(group,leader,face)
    return self.getGroupForMember(face)

  def translateSegment(self,segment,xForm):
    #TODO: make a more efficent version of this, would be easier if half-edge or
    #winged edge mesh. H-E: could traverse edges recursively, first going to sibling h-edge
    #stopping when the edge points to no other edge(naked),or to a face not in the segment,or
    #if the h-edge is part of the user-selected edge to be cut
    
    #collection = []
    for netEdge in self.flatEdges:
      if netEdge.fromFace in segment:
        #collection.append[netEdge]
        netEdge.translateGeom(self.flatVerts,xForm)
    #return collection


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
    
  def getFlatEdge(flatEdges,strField,value):
    flatEdges = FlatEdge.getFlatList(flatEdges)
    strField = strField.upper()
    

  '''DRAWING'''
  def drawEdges(self,netGroupName):
    collection = []
    for netEdge in self.flatEdges:
      collection.append(netEdge.drawEdgeLine(self.flatVerts))
    createGroup(netGroupName,collection)
