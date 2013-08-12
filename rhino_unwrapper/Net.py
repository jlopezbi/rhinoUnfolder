from segmentation import segmentIsland
from rhino_helpers import createGroup
class Net():
  def __init__(self):
    self.flatVerts = []
    self.flatEdges = []
    self.flatFaces = {}

    #self.groups,self.leaders = segmentIsland(self.flatFaces,[])
    
  def addEdge(self,flatEdge):
    self.flatEdges.append(flatEdge)
    return len(self.flatEdges)-1
  
  def addVert(self,flatVert):
    self.flatVerts.append(flatVert)
    return len(self.flatVerts)-1


  def segment(self,flatEdgeCut,xForm):
    assert(flatEdgeCut.type == 'fold')
    group,leader = segmentIsland(flatEdgeCut)
    self.updateIslands(group,leader)
    smallerSeg = self.getSmallerIsland()
    self.translate(smallerSeg)


  def updateNet(self,newGroups,newLeaders):
    self.replaceGroup(newGroups)
    self.resetLeaders(newLeaders)

  def replaceGroup(self,newGroups):
    pass

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
