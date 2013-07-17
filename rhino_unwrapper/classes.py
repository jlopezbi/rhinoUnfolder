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
      line_id = drawLine(points,color)
      self.line_id = line_id
    return line_id

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
  
  def getMidPoint(self):
    pntA = self.coordinates[0]
    pntB = self.coordinates[1]
    x = (pntA.X+pntB.X)/2.0
    y = (pntA.Y+pntB.Y)/2.0
    z = (pntA.Z+pntB.Z)/2.0
    return Rhino.Geometry.Point3f(x,y,z)


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
  def getFlatEdge(flatEdges,strField,value):
    flatEdges = FlatEdge.getFlatList(flatEdges)
    strField = strField.upper()
    if strField == 'EDGEIDX':
      assert(type(value)==int)
      for flatEdge in flatEdges:
        if flatEdge.edgeIdx == value:
          return flatEdge
    elif strField == 'LINE_ID':
      #assert guid?
      for flatEdge in flatEdges:
        if flatEdge.line_id == value:
          return flatEdge
    elif strField =='TYPE':
      assert(type(value)==str)
      for flatEdge in flatEdges:
        if flatEdge.type == value:
          return flatEdge
    return 

  @staticmethod
  def clearEdges(flatEdges):
    for flatEdge in flatEdges:
      flatEdge.clearAllGeom()

  @staticmethod
  def drawEdges(flatEdges,groupName):
    collection = []
    for flatEdge in flatEdges:
      collection.append(flatEdge.drawLine())
    createGroup(groupName,collection)




