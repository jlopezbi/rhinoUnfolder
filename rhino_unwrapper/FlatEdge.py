class FlatEdge():
  def __init__(self,_edgeIdx,_coordinates):
    # eventually add siblings data
    self.edgeIdx = _edgeIdx
    self.coordinates = _coordinates
    self.line_id = None
    self.geom = []
    self.type = None
    self.faceIdx = None

  

  def clearAllGeom(self):
    '''
    note: clear self.geom and self.line_id ?
    '''
    if self.line_id !=None:
      rs.DeleteObject(self.line_id)

    if len(self.geom)>0:
      for guid in self.geom:
        rs.DeleteObject(guid)
