from visualization import *

class FlatEdge():
  def __init__(self,_edgeIdx,_coordinates):
    self.edgeIdx = _edgeIdx
    self.coordinates = _coordinates #[[pntA,pntB],[pntA,pntB]]
    self.line_id = None
    self.geom = []
    self.type = None
    self.faceIdx = None

    self.hasTab = False
    self.tabAngles = []
    self.tabWidth = .5 #could be standard, or based on face area

  

  def drawLine(self):
    if self.coordinates != None:
      if self.type == 'fold':
        color = (0,49,224,61) #green
      elif self.type == 'cut':
        color = (0,237,43,120) #red
        if self.hasTab:
          color = (0,255,0,255) #magenta
      elif self.type == 'naked':
        color = (0,55,156,196) #blue
      points = self.coordinates
      line_id = drawLine(points,color,'None')
      self.line_id = line_id
    return line_id

  def drawTab(self):
    
    self.geom = geom
    return geom

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
  def getTabAngles(mesh,currFaceIdx,edgeIdx):
    otherFace = getOtherFaceIdx(edgeIdx,currFaceIdx,mesh)
    if otherFace:
      faceCenter = mesh.Faces.GetFaceCenter(otherFace) #Point3d
      posVecCenter = Rhino.Geometry.Vector3d(faceCenter) 

      pntI,pntJ = getPointsForEdge(mesh,edgeIdx) #Point3d
      vecEdge = getEdgeVector(mesh,edgeIdx) #Vector3d
      posVecI = Rhino.Geometry.Vector3d(pntI)
      posVecJ = Rhino.Geometry.Vector3d(pntJ)

      vecI = Rhino.Geometry.Vector3d.Subtract(posVecCenter,posVecI)
      vecJ = Rhino.Geometry.Vector3d.Subtract(posVecJ,posVecCenter)
      
      angleI = rs.VectorAngle(vecI,vecEdge)
      angleJ = rs.VectorAngle(vecJ,vecEdge)

      # color = (0,0,0,0)
      # drawVector(vecI,posVecI,color)
      # drawVector(vecJ,posVecCenter,color)
      # print #wtf: for some reason needed this line to print below
      # print( 'angleI: %.2f, angleJ: %.2f' %(angleI,angleJ) )

      return [angleI,angleJ]


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




