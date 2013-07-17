from visualization import *

class FlatEdge():
  def __init__(self,_edgeIdx,_coordinates):
    self.edgeIdx = _edgeIdx
    self.coordinates = _coordinates #[[pntA,pntB],[pntA,pntB]]
    self.line_id = None
    self.geom = []
    self.type = None
    self.faceIdx = None

  

  def drawLine(self):
    if self.coordinates != None:
      if self.type == 'fold':
        color = (0,49,224,61) #green
      elif self.type == 'cut':
        color = (0,237,43,120) #red
      elif self.type == 'naked':
        color = (0,55,156,196) #blue
      points = self.coordinates
    return drawLine(points,color)

  def clearAllGeom(self):
    '''
    note: clear self.geom and self.line_id ?
    '''
    if self.line_id !=None:
      rs.DeleteObject(self.line_id)
      self.line_id = None

    if len(self.geom)>0:
      for guid in self.geom:
        rs.DeleteObject(guid)

  @staticmethod
  def drawFlatEdges(flatEdges):
    net = []
    #flatten list
    flatEdges = FlatEdge.getFlatList(flatEdges)
    for flatEdge in flatEdges:
      #flatEdge.clearAllGeom()
      lineGuid = flatEdge.drawLine()
      net.append(lineGuid)
      flatEdge.line_id = lineGuid

    netGroupName = createGroup("net",net)

    return netGroupName

  @staticmethod
  def getFlatList(flatEdges):
    return [flatEdge for edgePair in flatEdges for flatEdge in edgePair]

  @staticmethod
  def getFlatEdgePair(flatEdges,strField,value):
    strField = strField.upper()
    if strField == 'EDGEIDX':
      assert(type(value)==int)
      for flatEdgePair in flatEdges:
        if flatEdgePair[0].edgeIdx == value:
          return flatEdgePair
    elif strField == 'LINE_ID':
      #assert guid?
      for flatEdgePair in flatEdges:
        if flatEdgePair[0].line_id == value:
          return flatEdgePair
    elif strField =='TYPE':
      assert(type(value)==str)
      for flatEdgePair in flatEdges:
        if flatEdgePair[0].type == value:
          return flatEdgePair
    else:
      return

  @staticmethod
  def clearEdges(flatEdges):
    for flatEdge in flatEdges:
      flatEdge.clearAllGeom()

  @staticmethod
  def drawEdges(flatEdges):
    for flatEdge in flatEdges:
      flatEdge.drawLine()




