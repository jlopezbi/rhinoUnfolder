from visualization import *
import math

#EDGE_GEOM_FUNCTIONS = {}

# def drawTab(flatEdge,color):
#   green = (0,49,224,61)
#   lineGuid = drawLine(flatEdge.coordinates,green)
#   return lineGuid
# EDGE_GEOM_FUNCTIONS['fold'] = drawFoldEdge

# def drawCutEdge(flatEdge):
#   red = (0,237,43,120)
#   lineGuid = drawLine(flatEdge.coordinates,red)
#   return lineGuid
# EDGE_GEOM_FUNCTIONS['cut'] = drawCutEdge

# def drawNakedEdge(flatEdge):
#   blue = (0,55,156,196)
#   lineGuid = drawLine(flatEdge.coordinates,blue)
#   return lineGuid
# EDGE_GEOM_FUNCTIONS['naked'] = drawNakedEdge

class FlatEdge():
  def __init__(self,_edgeIdx,_coordinates,_tVertIdxs): 
    self.edgeIdx = _edgeIdx
    self.coordinates = _coordinates
    self.tVertIdxs = _tVertIdxs
    self.line_id = None
    self.geom = []
    self.type = None
    self.faceIdxs = [] #if fold edge: [fromFace,toFace]

    self.tabOnLeft = False
    self.hasTab = False
    self.tabAngles = []
    self.tabWidth = .2 #could be standard, or based on face area

  

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
      line_id = drawLine(points,color,'None') #EndArrowhead
      self.line_id = line_id
    return line_id


  def drawTab(self):
    geom = []
    if len(self.tabAngles)<1:
      return
    pntA = self.coordinates[0]
    pntD = self.coordinates[1]
    vecA = Rhino.Geometry.Vector3d(pntA)
    vecD = Rhino.Geometry.Vector3d(pntD)

    alpha  = self.tabAngles[0]
    beta = self.tabAngles[1]

    lenI = self.tabWidth/math.sin(alpha*math.pi/180.0)
    lenJ = self.tabWidth/math.sin(beta*math.pi/180.0)

    if not self.tabOnLeft:
      alpha = -1*alpha
      beta = -1*beta

    vec = vecD.Subtract(vecD,vecA)
    vecUnit = rs.VectorUnitize(vec)
    vecI = rs.VectorScale(vecUnit,lenI)
    vecJ = rs.VectorScale(vecUnit,-lenJ)

    vecI = rs.VectorRotate(vecI,alpha,[0,0,1]) 
    vecJ = rs.VectorRotate(vecJ,-beta,[0,0,1])
    vecB = vecA + vecI
    vecC = vecD + vecJ

    pntB = Rhino.Geometry.Point3d(vecB)
    pntC = Rhino.Geometry.Point3d(vecC)

    points = [pntA,pntB,pntC,pntD]
    polyGuid = rs.AddPolyline(points)

    self.geom.append(polyGuid)
    return



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

  def setTabSide(self,foldEdges,foldEdgeIdx):
    '''
    occurs during LAYOUT
    '''
    assert(len(foldEdges[foldEdgeIdx])==1)
    foldEdge = foldEdges[foldEdgeIdx][0]
    testPoint = self.getNeighborCoordForCutEdge(foldEdge)
    if self.testPointIsLeft(testPoint):
      self.tabOnLeft = False
    else:
      self.tabOnLeft = True

  def testPointIsLeft(self,testPoint):
    '''
    use cross product to see if testPoint is to the left of 
    the edgLine
    returns False if co-linear. HOwever, if the mesh is triangulated
    and has no zero-area faces this should not occur.
    '''
    pntA = self.coordinates[0]
    pntB = self.coordinates[1]
    vecLine = getVectorForPoints(pntA,pntB)
    vecTest = Rhino.Geometry.Vector3d(testPoint)
    cross = Rhino.Geometry.Vector3d.CrossProduct(vecLine,vecTest)
    maxVal = cross.MaximumCoordinate #(pos and neg)
    return  maxVal > 0

  def getNeighborCoordForCutEdge(self,foldEdge):
    potentialCoords = foldEdge.coordinates
    for point in potentialCoords:
      if point not in self.coordinates:
        return point
    return

  # def getNeighborCoordForCutEdge(self,mesh,flatEdges):
  #   assert(self.type == 'cut'),"must be a cut edge"
  #   faceIdx = self.faceIdxs[0]
  #   tVert = self.tVertIdxs[0] #use I by defualt
  #   edgeIdxs = getFaceEdges(faceIdx,mesh)
  #   neighEdge = None
  #   for edgeIdx in edgeIdxs:
  #     if edgeIdx != self.edgeIdx:
  #       neighEdge = edgeIdx
  #   assert(type(neighEdge)==int),"neighEdge not assigned"

  #   potentialFlatEdges = flatEdges[neighEdge]
  #   neighFlatEdge = None
  #   for flatEdge in potentialFlatEdges:
  #     if faceIdx in flatEdge.edgeIdxs:
  #       neighFlatEdge = flatEdge

  #   potenitalCoords = neighFlatEdge.coordinates
  #   for point in potenitalCoords:
  #     if point not in self.coordinates:
  #       return point
  #   return

    #connectedEdges = get


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
      # strI = str(angleI)
      # strJ = str(angleJ)
      #rs.AddTextDot(strI,posVecI)
      #rs.AddTextDot(strJ,posVecJ)
      # print #wtf: for some reason needed this line to print below
      # print( 'angleI: %.2f, angleJ: %.2f' %(angleI,angleJ) )

      return [angleI,angleJ]



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

  @staticmethod
  def drawTabs(flatEdges,groupName):
    collection = []
    for flatEdge in flatEdges:
      if flatEdge.hasTab:
        collection.append(flatEdge.drawTab())
    createGroup(groupName,collection)

class FlatVert():
  def __init__(self,_edgeIdx,_coordinate,_tVertIdx): 
    self.edgeIdx = _edgeIdx
    self.coordinates = _coordinates
    self.tVertIdxs = _tVertIdxs
    self.line_id = None
    self.geom = []
    self.type = None
    self.faceIdxs = []

    self.tabOnLeft = False
    self.hasTab = False
    self.tabAngles = []
    self.tabWidth = .2 #could be standard, or based on face area



