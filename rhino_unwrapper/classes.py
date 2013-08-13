from visualization import *
import math




class FlatVert():
  def __init__(self,_tVertIdx,_point): 
    self.tVertIdx = _tVertIdx
    self.point = _point
    self.fromFace = None
    #self.toFace = None

    self.edgeIdx = None
    self.geom = []

  def hasSamePoint(self,point):
    return approxEqual(self.point.X,point.X) and approxEqual(self.point.Y,point.Y)

  def translate(self,xForm):
    self.point.Transform(xForm)

class FlatEdge():
  def __init__(self,_edgeIdx,vertI,vertJ): 
    self.edgeIdx = _edgeIdx
    self.I = vertI
    self.J = vertJ
    
    self.line = None
    self.line_id = None
    self.geom = []
    self.type = None
    #self.faceIdxs = [] #if fold edge: [fromFace,toFace]
    self.fromFace = None
    self.toFace = None

    self.tabOnLeft = False
    self.hasTab = False
    self.tabAngles = []
    self.tabWidth = .2 #could be standard, or based on face area

  def update(self,newVertSpecs):
    newVerts = newVertSpecs.keys()
    for vert in self.tVertIdxs:
      if vert in newVerts:
        self.tVertSpecs[vert] = newVertSpecs[vert]

  def getCoordinates(self,flatVerts):
    vertI,vertJ = self.getFlatVerts(flatVerts)
    return [vertI.point,vertJ.point]

  def getFlatVerts(self,flatVerts):
    flatVertI = flatVerts[self.I]
    flatVertJ = flatVerts[self.J]
    return (flatVertI,flatVertJ)

  def getTVerts(self,mesh):
    return getTVertsForEdge(mesh,self.edgeIdx)

  def drawEdgeLine(self,flatVerts):
    if self.type != None:
      if self.type == 'fold':
        color = (0,49,224,61) #green
      elif self.type == 'cut':
        color = (0,237,43,120) #red
        if self.hasTab:
          color = (0,255,0,255) #magenta
      elif self.type == 'naked':
        color = (0,55,156,196) #blue
      points = self.getCoordinates(flatVerts)
      line_id,line = drawLine(points,color,'None') #EndArrowhead
      self.line_id = line_id
      self.line = line
    return line_id

  def translateGeom(self,flatVerts,xForm):
    self.translateEdgeLine(xForm)
    self.translateNetVerts(flatVerts,xForm)

  def translateEdgeLine(self,xForm):
    if self.line != None:
      self.line.Transform(xForm)
      scriptcontext.doc.Objects.Replace(self.line_id,self.line)

  def translateNetVerts(self,flatVerts,xForm):
    netVertI,netVertJ = self.getFlatVerts(flatVerts)
    netVertI.translate(xForm)
    netVertJ.translate(xForm)

  def drawTab(self,flatVerts):
    if len(self.tabAngles)<1:
      self.drawTriTab(flatVerts)
    else:
      self.drawQuadTab(flatVerts)
      
  def drawQuadTab(self,flatVerts):
    pntA,pntD = self.getCoordinates(flatVerts)
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

  def drawTriTab(self,flatVerts):
    pntA,pntC = self.getCoordinates(flatVerts)
    pntB = self.tabFaceCenter

    points = [pntA,pntB,pntC]
    polyGuid = rs.AddPolyline(points)
    self.geom.append(polyGuid)

  def clearAllGeom(self):
    '''
    note: clear self.geom and self.line_id ?
    '''
    if self.line_id !=None:
      scriptcontext.doc.Objects.Delete(self.line_id,True)
      self.line_id = None

    if len(self.geom)>0:
      for guid in self.geom:
        scriptcontext.doc.Objects.Delete(guid,True)
  
  def getMidPoint(self,flatVerts):
    coordinates = self.getCoordinates(flatVerts)
    pntA = coordinates[0]
    pntB = coordinates[1]
    x = (pntA.X+pntB.X)/2.0
    y = (pntA.Y+pntB.Y)/2.0
    z = (pntA.Z+pntB.Z)/2.0
    return Rhino.Geometry.Point3f(x,y,z)

  def getFaceFromPoint(self,net,point):
    #TODO: fails for horizontal lines :(
    assert(self.type =='fold')
    faceA = self.fromFace
    faceB = self.toFace
    leftA = self.testFacesIsLeft(net,faceA)
    leftB = self.testFacesIsLeft(net,faceB)
    assert(leftA!=leftB),"both faces found to be on same side of edge"
    leftPoint = self.testPointIsLeft(point,net.flatVerts)
    if leftA==leftPoint:
      return faceA
    elif leftB==leftPoint:
      return faceB
    print "unable to find face"
    return 

  def testFacesIsLeft(self,net,face):
    '''find which side the face is on relative to this edge
    ouput: 1 for left, -1 for right, 0 for error
    '''

    testPoint = net.flatVerts[self.getNeighborFlatVert(net,face)].point
    if not testPoint:
      return -1
    return self.testPointIsLeft(testPoint,net.flatVerts)
    
  
  def setTabSide(self,net):
    '''
    occurs during LAYOUT
    '''
  
    testPoint = net.flatVerts[self.getNeighborFlatVert(net)].point
    if self.testPointIsLeft(testPoint,net.flatVerts):
      self.tabOnLeft = False
    else:
      self.tabOnLeft = True

  def testPointIsLeft(self,testPoint,flatVerts):
    '''
    use cross product to see if testPoint is to the left of 
    the edgLine
    returns False if co-linear. HOwever, if the mesh is triangulated
    and has no zero-area faces this should not occur.
    '''
    pntA,pntB = self.getCoordinates(flatVerts)
    vecLine = getVectorForPoints(pntA,pntB)
    vecTest = getVectorForPoints(pntA,testPoint)#this may be too skewed
    cross = Rhino.Geometry.Vector3d.CrossProduct(vecLine,vecTest)
    z = cross.Z #(pos and neg)
    return  z > 0 

  def getNeighborFlatVert(self,net,face=None):
    '''
    gets one of the flatVerts associated with the given
    face, but that is not a part of this flatEdge.
    if face==None uses the fromFace associated with this edge
    '''

    if face==None:
      face = self.fromFace
    tVertsEdge = set([self.I,self.J])
    flatFace = net.flatFaces[face]
    tVertsFace = set(flatFace.vertices)
    neighbors = list(tVertsFace-tVertsEdge)
    return neighbors[0] #arbitrarily return first tVert

  def getTabAngles(self,mesh,currFaceIdx,xForm):
    edge = self.edgeIdx
    otherFace = getOtherFaceIdx(edge,currFaceIdx,mesh)

    if otherFace != None:
      faceCenter = mesh.Faces.GetFaceCenter(otherFace) #Point3d
      if getDistanceToEdge(mesh,edge,faceCenter)<=self.tabWidth:
        faceCenter.Transform(xForm)
        self.tabFaceCenter = faceCenter
        return
      posVecCenter = Rhino.Geometry.Vector3d(faceCenter) 

      pntI,pntJ = getPointsForEdge(mesh,edge) #Point3d
      vecEdge = getEdgeVector(mesh,edge) #Vector3d
      posVecI = Rhino.Geometry.Vector3d(pntI)
      posVecJ = Rhino.Geometry.Vector3d(pntJ)

      vecI = Rhino.Geometry.Vector3d.Subtract(posVecCenter,posVecI)
      vecJ = Rhino.Geometry.Vector3d.Subtract(posVecJ,posVecCenter)
      
      angleI = rs.VectorAngle(vecI,vecEdge)
      angleJ = rs.VectorAngle(vecJ,vecEdge)

      self.tabAngles = [angleI,angleJ]

      # color = (0,0,0,0)
      # drawVector(vecI,posVecI,color)
      # drawVector(vecJ,posVecCenter,color)
      # strI = str(angleI)
      # strJ = str(angleJ)
      #rs.AddTextDot(strI,posVecI)
      #rs.AddTextDot(strJ,posVecJ)
      # print #wtf: for some reason needed this line to print below
      # print( 'angleI: %.2f, angleJ: %.2f' %(angleI,angleJ) )

      #return [angleI,angleJ]




  @staticmethod
  def clearEdges(flatEdges):
    for flatEdge in flatEdges:
      flatEdge.clearAllGeom()

  @staticmethod
  def drawEdges(flatVerts,flatEdges,groupName):
    collection = []
    for flatEdge in flatEdges:
      collection.append(flatEdge.drawEdgeLine(flatVerts))
    createGroup(groupName,collection)

  @staticmethod
  def drawTabs(flatVerts,flatEdges,groupName):
    collection = []
    for flatEdge in flatEdges:
      if flatEdge.hasTab:
        collection.append(flatEdge.drawTab(flatVerts))
    createGroup(groupName,collection)

class FlatFace():
  #does not store meshFace because position in dict determines this
  def __init__(self,_vertices,_fromFace):
    self.vertices = _vertices # a list of netVerts
    self.fromFace = _fromFace


  def getFlatVerts(self,flatVerts):
    tVerts = self.vertices.keys()
    collection = []
    for vert in tVerts:
      col = self.vertices[vert]
      collection.append(flatVerts[vert][col])
    return collection

  def getFlatVertForTVert(self,tVert,flatVerts):
    assert(tVert in self.vertices.keys())
    return flatVerts[tVert][self.vertices[tVert]]

  def reAssignVerts(self,newVertSpecs):
    tVerts = newVertSpecs.keys()
    for tVert in tVerts:
      if tVert in self.vertices.keys():
        self.vertices[tVert] = newVertSpecs[tVert]


  
