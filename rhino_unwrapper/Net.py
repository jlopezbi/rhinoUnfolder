from segmentation import segmentIsland

class Net():
  def __init__(self,_flatVerts,_flatEdges,_flatFaces):
    self.flatVerts = _flatVerts
    self.flatEdges = _flatEdges
    self.flatFaces = _flatFaces

    self.groups,self.leaders = segmentIsland(self.flatFaces,[])
    


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