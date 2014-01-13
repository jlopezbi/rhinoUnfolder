from visualization import *
from transformations import transformToXY
import math,copy

class FlatVert():
  def __init__(self,_tVertIdx,_point): 
    self.tVertIdx = _tVertIdx
    self.point = Rhino.Geometry.Point3d(_point) #clobbber to point3d
    self.fromFace = None
    #self.toFace = None

    self.edgeIdx = None
    self.geom = []

  def hasSamePoint(self,point):
    return approxEqual(self.point.X,point.X) and approxEqual(self.point.Y,point.Y)

  def translate(self,xForm,copy=False):
    '''
    translate the flatVert's point by xForm, if copy=True: simply return a new transformed point
    '''
    if copy:
      newPnt = Rhino.Geometry.Point3d(self.point)
      newPnt.Transform(xForm)
      return newPnt
    else:
      self.point.Transform(xForm)
      return self.point

class FlatEdge():
  def __init__(self,_edgeIdx,vertI,vertJ): 
    self.edgeIdx = _edgeIdx #edgeIdx in mesh
    self.I = vertI #netVertIdx
    self.J = vertJ #netVertIdx
    #self.reverseOrderForNet = reverseOrderForNet #ordering for the net and the mesh may not be the same. so store it
    
    self.line = None
    self.line_id = None
    self.geom = [] #all geometry associated with this edge
    self.type = None
    self.fromFace = None #faces have direct mapping (this is netFace and meshFace)
    self.toFace = None
    self.angle = None

    '''JOINERY'''
    self.tabOnLeft = None #important for general joinery drawing
    
    '''Tabs'''
    self.hasTab = False
    self.tabFaceCenter = None #point3d
    self.tabAngles = []
    self.tabWidth = .5 #could be standard, or based on face area

    '''Holes'''
    self.distI = None
    self.distJ = None

    '''BUCKEL HACK FOR LG'''
    self.hasOffset = False

  def reset(self,oldVert,newVert):
    if self.I==oldVert:
      self.I=newVert
    elif self.J==oldVert:
      self.J=newVert
    else:
      assert(False==True), "error, flatEdge does not have oldVert"

  '''SELF INFO'''

  def getCoordinates(self,flatVerts):
    vertI,vertJ = self.getFlatVerts(flatVerts)
    return [vertI.point,vertJ.point]

  def getFlatVerts(self,flatVerts):
    flatVertI = flatVerts[self.I]
    flatVertJ = flatVerts[self.J]
    return (flatVertI,flatVertJ)

  def getFlatFace(self,flatFaces):
    return flatFaces[self.fromFace]

  def getNetVerts(self):
    return (self.I,self.J)

  def getTVerts(self,mesh):
    return getTVertsForEdge(mesh,self.edgeIdx)

  def getMeshAngle(self,mesh):
    '''get angle of the corresponding mesh edge'''
    if self.angle==None:
      edge = self.edgeIdx
      faceIdxs = getFacesForEdge(mesh, edge)
      if (len(faceIdxs)==2):
        faceNorm0 = mesh.FaceNormals.Item[faceIdxs[0]]
        faceNorm1 = mesh.FaceNormals.Item[faceIdxs[1]]
        self.angle = Rhino.Geometry.Vector3d.VectorAngle(faceNorm0,faceNorm1) 
        return self.angle
      else:
        return None
    else:
      return self.angle

  def getLength(self,flatVerts):
    pntA,pntB = self.getCoordinates(flatVerts)
    return getVectorForPoints(pntA,pntB).Length

  def getEdgeVec(self,flatVerts):
    pointI = flatVerts[self.I].point
    pointJ = flatVerts[self.J].point
    return Rhino.Geometry.Vector3d(pointJ-pointI)

  def getEdgeLine(self,net):
    if self.line==None:
      pntI,pntJ = self.getCoordinates(net.flatVerts)
      return Rhino.Geometry.Line(pntI,pntJ)
    else:
      return self.line

  '''DRAWING'''
  def clearAllGeom(self):
    '''
    note: clear self.geom and self.line_id ?
    '''
    if self.line_id !=None:
      scriptcontext.doc.Objects.Delete(self.line_id,True)
      self.line_id = None

    if len(self.geom)>0:
      rs.DeleteObjects(self.geom)
      # for guid in self.geom:
      #   scriptcontext.doc.Objects.Delete(guid,True) 
        #TODO: PROBLEM HERE: 
        #Multiple targets could match: Delete(ObjRef, bool), Delete(RhinoObject, bool), Delete(IEnumerable[Guid], bool)

  def drawNetEdge(self,net):
    '''
    Highest level drawing: draws all geometry associated with edge
    Assumes that all flatEdge geom has already been removed
    Draws all geometry for netEdge:
      -edgeLine
      -Tabs
      -offsets
      -holes
    '''
    group = rs.AddGroup() # create a sub-group for each edge
    geom = self.geom
    self._addGeom(self.drawEdgeLine(net.flatVerts,net.angleThresh,net.mesh))
    #geom.append(self.drawEdgeLine(net.flatVerts,net.angleThresh,net.mesh))
    #ASSUME: that each face has at least one fold edge (could not be true because of user-cuts or
    #segmentation)  
    '''
    if self.type=='fold' or self.type=='naked':
      offsetXForm,lineGuid,oppositeEdge = self._drawOffset(net)
      oppositeEdge._drawOffset(net)
      oppositeEdge.hasOffset= True
      self.hasOffset = True 
    '''
    if net.drawTabs and self.type=='cut':
      polyGuid,polyCurve = self.drawTab(net)
      if self.hasOffset:
        polyCurve.Transform(self.offsetXForm)
        scriptcontext.doc.Objects.Replace(polyGuid,polyCurve)
      self._addGeom(polyGuid)

    if net.drawFaceHoles:
      self._addGeom(self.drawFaceHole(net))
    
    grouped =  rs.AddObjectsToGroup(geom,group)
    return geom

  def drawEdgeLine(self,flatVerts,angleThresh,mesh):
    if self.type != None:
      if self.type == 'fold':
        if self.getMeshAngle(mesh)>=angleThresh:
          color = (0,49,224,61) #green
        else:
          color = (0,161,176,181) #bluegreyish for no crease lines
      elif self.type == 'cut':
        color = (0,237,43,120) #red
        if self.hasTab:
          color = (0,255,0,255) #magenta
      elif self.type == 'naked':
        color = (0,55,156,196) #blue
      elif self.type == 'contested':
        color = (0,255,115,0) #orange
      points = self.getCoordinates(flatVerts)
      if self.line_id!=None: #just in case clearing geom did not get perfomed
        scriptcontext.doc.Objects.Delete(self.line_id,True)
      lineGuid,line = drawLine(points,color,'None') #EndArrowhead StartArrowhead
      self.line_id = lineGuid
      self.line = line
    return lineGuid

  def _drawEdgeLineNoMesh(self,color,flatVerts):
    '''
    for testing
    '''
    points = self.getCoordinates(flatVerts)
    line_id,line = drawLine(points,color,'None') #EndArrowhead StartArrowhead
    return line_id

  def _getOffsetEdgeLine(self,net,flatface,draw=False):
    xForm = self._computeOffsetXForm(net,flatface)
    copy = True
    lineGuid,line =  self._translateEdgeLine(net,xForm,draw,copy)
    if lineGuid:
      self._addGeom(lineGuid)
    self.offsetXForm = xForm
    self.offsetLine = line #save this line to this flatEdge for later use
    return xForm,line,lineGuid


  def _computeOffsetXForm(self,net,flatFace):
    '''
    compute offset xForm for this edge, given a flatface (fold edges have two flatFaces)
    ouput:
      xForm = transform for this edge line
    '''
    buckleVal = net.buckleVals[flatFace.faceIdx]
    scale = net.buckleScale
    oppositeEdge = self.getOppositeFlatEdge(net,flatFace)
    assert(oppositeEdge!=-1),"did not find oppositeEdge (maybe triangle face)"

    oppositeMidPnt = oppositeEdge.getMidPoint(net.flatVerts)
    midPnt = self.getMidPoint(net.flatVerts)
    faceVec = getVectorForPoints(oppositeMidPnt,midPnt)
    lengthFace = faceVec.Length

    faceVec.Unitize()
    offsetVec = faceVec*(scale*buckleVal*lengthFace/2.0) #half for each side
    #drawVector(offsetVec,midPnt,(0,255,255,255))

    xForm = Rhino.Geometry.Transform.Translation(offsetVec)

    if xForm:
      return xForm
    else:
      print "did not create xForm in _computeOffsetXForm"
      return




  def _addGeom(self,guid):
    assert(str(type(guid))== "<type 'Guid'>"), "attempt to added not guid geom"
    self.geom.append(guid)
    

  '''TRANSLATION'''

  def resetFromFace(self,segmentFace):
    '''
    specific to segmentation:
    set the from face of this edge, which is the user-selected edge to perform segmentation,
    to be the face NOT in the segment (ie not the segmentFace)
    '''
    if self.fromFace == segmentFace:
      self.fromFace = self.toFace
      return self.toFace
    return self.fromFace

  def translateGeom(self,movedNetVerts,flatVerts,xForm):
    #self.translateEdgeLine(xForm)
    self.translateNetVerts(movedNetVerts,flatVerts,xForm)
    if self.tabFaceCenter!=None:
      self.tabFaceCenter.Transform(xForm)

  def _translateEdgeLine(self,net,xForm,draw=False,copy=False,):
    '''
    translates this edgeLine by xForm
    input:
      net = instance of Net()
      xForm = transform to translate edge line by 
      draw = boolean deciding wether or not to draw the translated edgeLine
      copy = boolean deciding wether to make a copy, i.e. preserve the original edgeline, or
             to replace it
    ouput:
      lineGuid = guid for the new geometry (None if no geometry added (draw=False))
      line = a Rhino.Geometry.Line instance; the translated line
    '''
    originalLine = self.getEdgeLine(net)
    lineGuid = None
    if copy:
      line = Rhino.Geometry.Line(originalLine.From,originalLine.To) #make copy of edge line
      line.Transform(xForm)
      if draw:
        lineGuid = scriptcontext.doc.Objects.AddLine(line)

    else:
      line = originalLine
      line.Transform(xForm)
      if draw:
        lineGuid = scriptcontext.doc.Objects.Replace(self.line_id,originalLine)

    return lineGuid,line


  def translateTabFaceCenter(self,xForm):
    if self.tabFaceCenter!=None:
      self.tabFaceCenter.Transform(xForm)

  def translateNetVerts(self,movedNetVerts,flatVerts,xForm):
    netVertI,netVertJ = self.getFlatVerts(flatVerts)
    if netVertI not in movedNetVerts:
      netVertI.translate(xForm)
      movedNetVerts.append(netVertI)
    if netVertJ not in movedNetVerts:
      netVertJ.translate(xForm)
      movedNetVerts.append(netVertJ)

  '''JOINERY'''
  def drawTab(self,net):

    '''
    drawTab joinery:
    outputs guid for polyline
    '''
    #TODO: remove this clearing of geom: unnecessary
    # if len(self.geom)>0:
    #   for guid in self.geom:
    #     scriptcontext.doc.Objects.Delete(guid,True)
    if len(self.tabAngles)<1:
      #return self._drawTruncatedTab(net)
      poly_id,polylineCurve = self._drawAngleTab(net.flatVerts,net.tabAngle)
      return poly_id,polylineCurve
      #return self._drawTriTab(net)
    else:
      return self._drawQuadTab(net.flatVerts)
      
  def _drawQuadTab(self,flatVerts):
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

    polylineCurve =  getPolylineCurve(points)
    poly_id,polylineCurve = drawCurve(polylineCurve)
    return poly_id,polylineCurve

  def _drawAngleTab(self,flatVerts,angle,xForm=None):
    '''
    draw a truncated tab in the style of pepakura:
    constant tabWidth, constant inner angles
    input:
      flatVerts = list of FlatVerts instances
      angle = angle in radians for the inner angles of the tab. for now let this be a net-wide property
    '''
    #         T
    #    B-------C  
    #   /         \
    #  /           \
    # A->x-------x<-D
    # TODO: write this function, use tabFace center to set the side of the tab
    # methinks


    pntA,pntD = self.getCoordinates(flatVerts)
    #print "type: " + str(type(pntA))
    pntT = self.tabFaceCenter
    assert(pntT!=None), "need a tabFaceCenter to make a tab"

    vecDiag = Rhino.Geometry.Vector3d(pntT-pntA)
    vecEdge = Rhino.Geometry.Vector3d(pntD-pntA)


    vecClosestPnt = projectVector(vecDiag,vecEdge)
    vecPerp = Rhino.Geometry.Vector3d(vecDiag - vecClosestPnt)
    vecPerp.Unitize()
    vecTabWidth = vecPerp*self.tabWidth
    x = self.tabWidth/math.tan(angle)

    #This means the edge is to short for a truncated tab:
    #make a traingular tab instead
    if (vecEdge.Length <= 2.0*x):
      pntMid = getMidPointPoints(pntA,pntD)
      pntE = Rhino.Geometry.Point3d(vecTabWidth+pntMid)

      points = [pntA,pntE,pntD]

    else:
      vecEdge.Unitize()

      vecEdgeAD = vecEdge*x 
      vecEdgeDA = vecEdge*-x

      vecB = vecTabWidth+vecEdgeAD
      vecC = vecTabWidth+vecEdgeDA

      pntB = Rhino.Geometry.Point3d(pntA+vecB)
      pntC = Rhino.Geometry.Point3d(pntD+vecC)

      points = [pntA,pntB,pntC,pntD]

    polylineCurve =  getPolylineCurve(points)
    poly_id,polylineCurve = drawCurve(polylineCurve)
    return poly_id,polylineCurve

  def test_drawAngleTab(self):
    print "MEOW"

  def _drawTruncatedTab(self,net):
    '''
    draw a truncated tab using the drawing style of triTab, but with an offset-line intersection
    '''
    tabLen = self.tabWidth
    flatVerts = net.flatVerts
    flatFaces = net.flatFaces
    I,J = self.getCoordinates(flatVerts)
    K = self.tabFaceCenter
    if self.tabFaceCenter ==None: #this is ahack: TODO: if a new cut edge is created, give it a tabFaceCenter
      return
    diagA = Rhino.Geometry.Line(I,K)
    diagB = Rhino.Geometry.Line(J,K)
    offsetLine, vecA = getOffset((I,J),K,tabLen,True) 

    resultI,aI,bI = Rhino.Geometry.Intersect.Intersection.LineLine(offsetLine,diagA)
    resultJ,aJ,bJ = Rhino.Geometry.Intersect.Intersection.LineLine(offsetLine,diagB)
    if  resultI and resultJ:
      intersectPntI = offsetLine.PointAt(aI)
      intersectPntJ = offsetLine.PointAt(aJ)
      
      shorterThanTab = self._checkIfShortTab(net)
      if shorterThanTab == 1:
        points = [I,intersectPntJ,intersectPntI,J] #flip order to avoid self-intersction
      elif shorterThanTab == 0:
        point = [I,K,J]
      elif shorterThanTab == -1:
        points = [I,intersectPntI,intersectPntJ,J] #order is as expected


      lineA = Rhino.Geometry.Line(I,intersectPntI)
      lineB = Rhino.Geometry.Line(J,intersectPntJ)

    else:
      points = [I,K,J]

    polyGuid = rs.AddPolyline(points)
    self.geom.append(polyGuid)

    return polyGuid

  def _checkIfShortTab(self,net):
    center = self.tabFaceCenter
    edgeLine =  self.getEdgeLine(net)
    closestPnt = edgeLine.ClosestPoint(center,True)
    vec = Rhino.Geometry.Point3d.Subtract(center,closestPnt)
    lenVec = vec.Length
    if lenVec < self.tabWidth:
      return 1
    if lenVec == self.tabWidth:
      return 0
    else:
      return -1

  def _drawTriTab(self,net):
    holeRadius = net.holeRadius
    mesh = net.mesh
    flatVerts = net.flatVerts
    flatFaces = net.flatFaces

    minArea = (holeRadius**2.0)*math.pi*30
    #print "minArea: " + str(minArea)

    flatFace = self.getConnectToFace(flatFaces,mesh)
    area = flatFace.getArea(flatVerts)

    pntA,pntC = self.getCoordinates(flatVerts)
    pntB = self.tabFaceCenter

    points = [pntA,pntB,pntC]
    polyline = Rhino.Geometry.PolylineCurve([pntA,pntB,pntC,pntA])
    props = Rhino.Geometry.AreaMassProperties.Compute(polyline)
    if area > minArea:
      centerPnt = props.Centroid
    else:
      rs.AddTextDot("o",pntB)
      centerPnt = flatFaces[self.fromFace].getCenterPoint(flatVerts,True)
    hole = rs.AddCircle(centerPnt,holeRadius)
    polyGuid = rs.AddPolyline(points)
    self.geom.append(polyGuid)
    self.geom.append(hole)
    return polyGuid

  def drawFaceHole(self,net):
    holeRadius = net.holeRadius
    pntA,pntC = self.getCoordinates(net.flatVerts)
    pntB = net.flatFaces[self.fromFace].getCenterPoint(net.flatVerts,True)
    pnts = [pntA,pntB,pntC,pntA]
    polyline = Rhino.Geometry.PolylineCurve(pnts)
    props = Rhino.Geometry.AreaMassProperties.Compute(polyline)
    centerPnt = props.Centroid
    hole = rs.AddCircle(centerPnt,holeRadius)
    self.geom.append(hole)

  def drawHoles(self,net,connectorDist,safetyRadius,holeRadius):
    self.assignHoleDists(net,connectorDist,safetyRadius)
    points = self.getHolePoints(net.flatVerts)
    safeR = holeRadius+(safetyRadius-holeRadius)/2.0
    geom = [[0,0],[0,0]]
    for i, point in enumerate(points):
      if point!=None:
        geom[i][0] = Rhino.Geometry.Circle(point,holeRadius)
        circleSafe = Rhino.Geometry.Circle(point,safeR)
        geom[i][1] = Rhino.Geometry.ArcCurve(circleSafe)
    if geom[0][0]!=0 and geom[1][0]!=0:
      tolerance = .001
      plane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0),Rhino.Geometry.Vector3d(0,0,1))

      #check if the circles are inside there parent face

      #check if the circles are intersectin each other
      relation = Rhino.Geometry.Curve.PlanarClosedCurveRelationship(geom[0][1],geom[1][1],plane,tolerance)
      if relation==Rhino.Geometry.RegionContainment.Disjoint:
        guidI = scriptcontext.doc.Objects.AddCircle(geom[0][0])
        guidJ = scriptcontext.doc.Objects.AddCircle(geom[1][0])
        
        #draw lines for debugging
        centerPnt = geom[0][0].Center
        rs.AddLine(centerPnt,self.line.ClosestPoint(centerPnt,True))

        centerPnt = geom[1][0].Center
        rs.AddLine(centerPnt,self.line.ClosestPoint(centerPnt,True))

        self.geom.extend((guidI,guidJ))
      elif relation==Rhino.Geometry.RegionContainment.MutualIntersection:
        #only add I circle
        guid = scriptcontext.doc.Objects.AddCircle(geom[0][0])
        self.geom.append(guid)
    elif geom[0][0]!=0:
      guid = scriptcontext.doc.Objects.AddCircle(geom[0][0])
      self.geom.append(guid)
    elif geom[1][0]!=0:
      guid = scriptcontext.doc.Objects.AddCircle(geom[1][0])
      self.geom.append(guid)

  def circleIsInFace(self,net,circle):
    # faceForEdge = 
    # faceBoundary = net.
    pass

  '''GET INFO'''
  def getOffsetCorrectOrientation(self):
    '''
    assumes that an offset line has been created ya
    ''' 
    if self.reverseOrderForNet==True:
      print "meow"
      return Rhino.Geometry.Line(self.offsetLine.To,self.offsetLine.From)
    else:
      print "cow"
      return self.offsetLine

  def getConnectToFace(self,flatFaces,mesh):
    return flatFaces[getOtherFaceIdx(self.edgeIdx,self.fromFace,mesh)]

  def getTabFaceCenter(self,mesh,currFace,xForm):
    otherFace = getOtherFaceIdx(self.edgeIdx,currFace,mesh)
    if otherFace!=None and otherFace != -1:
      faceCenter = mesh.Faces.GetFaceCenter(otherFace)
      self.tabFaceCenter = transformToXY(faceCenter,xForm)
    if self.tabFaceCenter==None:
      return False
    else:
      return True

  def getHolePoints(self,flatVerts):
    #TODO: replace this with less redundant version (iterate trhough points)
    pointI,pointJ = (None,None)
    if self.distI!=-1:
      vecI = self.getEdgeVec(flatVerts)
      vecI.Unitize()
      vecI = vecI*self.distI
      pointI = (flatVerts[self.I].point+vecI)
      pointI = pointI+self.holeVec
    if self.distJ!=-1:  
      vecJ = -1*self.getEdgeVec(flatVerts)
      vecJ.Unitize()
      vecJ = vecJ*self.distJ
      pointJ = (flatVerts[self.J].point+vecJ)
      pointJ = pointJ+self.holeVec
    return (pointI,pointJ)

  def assignHoleDists(self,net,connectorDist,safetyRadius):
    if self.distI==None and self.distJ==None:
      pair = net.flatEdges[self.pair]
      distsA = pair.getHoleDistances(net,connectorDist,safetyRadius)
      distsB = self.getHoleDistances(net,connectorDist,safetyRadius)
      distI = max(distsA[0],distsB[0])
      distJ = max(distsA[1],distsB[1])
      
      pair.distI = distI
      pair.distJ = distJ
      pair.holeVec = distsA[2]
      self.distI = distI
      self.distJ = distJ
      self.holeVec = distsB[2]

  def assignHoleDistsRatio(self,flatVerts,ratio):
    edgeVec = self.getEdgeVec(flatVerts)
    length = edgeVec.Length
    distI = length*ratio 
    distJ = length*ratio
    return (distI,distJ,vec)

  def getHoleDistancesSimple(self,net,connectorDist,ratioEdgeLen):
    edgeVec = self.getEdgeVec(net.flatVerts)

  def getHoleDistances(self,net,connectorDist,safetyRadius):
    '''
    get the two distances for a given edge by interescting the offset lines
    from the edge line and the two lines formed from the edgePoints to faceCenter
    '''
    flatVerts = net.flatVerts
    flatFaces = net.flatFaces
    axis = Rhino.Geometry.Vector3d(0.0,0.0,1.0) #assumes laying-out in xy plane
    K = self.getFacePoint(flatVerts,flatFaces) #CenterPoint
    #rs.AddPoint(K)
    I,J = self.getCoordinates(flatVerts)
    offsetLineA, vecA = getOffset((I,J),K,connectorDist,True) #EdgeOffset
    offsetLineB, vecB = getOffset((I,K),J,safetyRadius, True)
    offsetLineC, vecC = getOffset((J,K),I,safetyRadius, True)
      
    rcI,aI,bI = Rhino.Geometry.Intersect.Intersection.LineLine(offsetLineA,offsetLineB)
    if not rcI:
      print "No Intersection found for first chordB"
      return Rhino.Commands.Result.Nothing
    rcJ,aJ,bJ = Rhino.Geometry.Intersect.Intersection.LineLine(offsetLineA,offsetLineC)
    if not rcJ:
      print "No Intersection found for second chordC"
      return Rhino.Commands.Result.Nothing
    pointI = offsetLineA.PointAt(aI)
    pointJ = offsetLineA.PointAt(aJ)
    #CHECK IF POINTS ARE WITHIN THAT FACE
    if self.line==None: self.line = Rhino.Geometry.Line(I,J)

    if not self.inFace(net,pointI):
      print "assining -1"
      distI = -1
    else:
      pntOnEdgeI = self.line.ClosestPoint(pointI,True)
      distI = pntOnEdgeI.DistanceTo(I)

    if not self.inFace(net,pointJ):
      distJ = -1
    else:
      pntOnEdgeJ = self.line.ClosestPoint(pointJ,True)
      distJ = pntOnEdgeJ.DistanceTo(J)    
    #rs.AddPoint(pntOnEdgeI)
    #rs.AddPoint(pntOnEdgeJ)
    return (distI,distJ,vecA) #vecA will be used to place actually hole

  def getFacePoint(self,flatVerts,flatFaces):
    '''
    get the center point of this edges's fromFace
    '''
    return flatFaces[self.fromFace].getCenterPoint(flatVerts)

  def getFacePolyline(self,net):
    '''
    get the polyline curve for this edges' face
    '''
    polylineCurve = net.flatFaces[self.fromFace].getPolylineCurve(net.flatVerts)
    return polylineCurve

  def getFaceMidVec(self,net):
    '''
    get the vector from the center of this edges fromFace, to the midpoint of this edge
    '''
    centerPnt = self.getFacePoint(net.flatVerts,net.flatFaces)
    midPnt = Rhino.Geometry.Point3d(self.getMidPoint(net.flatVerts))
    return Rhino.Geometry.Vector3d(midPnt-centerPnt)

  def inFace(self,net,point):
    polylineCurve = self.getFacePolyline(net)
    relationship = polylineCurve.Contains(point)
    if Rhino.Geometry.PointContainment.Unset==relationship:
      print "curve was not closed, relationship meaningless"
      return
    elif Rhino.Geometry.PointContainment.Inside==relationship:
      return True
    elif Rhino.Geometry.PointContainment.Outside==relationship:
      return False
    else:
      #coincident, still leads to bad condition for holes
      return False
  
  def getMidPoint(self,flatVerts):
    coordinates = self.getCoordinates(flatVerts)
    pntA = coordinates[0]
    pntB = coordinates[1]
    x = (pntA.X+pntB.X)/2.0
    y = (pntA.Y+pntB.Y)/2.0
    z = (pntA.Z+pntB.Z)/2.0
    return Rhino.Geometry.Point3f(x,y,z)

  def getFaceFromPoint(self,net,point):
    '''return the face that corresponds to the point that a use seleceted to translate the segment to
    '''
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
  
  def setTabSide(self,facePoint,flatVerts):
    '''
    occurs affter complete layout
    '''
    if self.tabOnLeft == None:
      #testPoint = net.flatVerts[self.getNeighborFlatVert(net)].point
      if self.testPointIsLeft(facePoint,flatVerts):
        self.tabOnLeft = False
      else:
        self.tabOnLeft = True
      return self.tabOnLeft
    else:
      return self.tabOnLeft

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

  def getTabAngles(self,mesh,currFaceIdx,xForm):
    #WORKING AWAY FROM THIS: data is implicit in 
    edge = self.edgeIdx
    otherFace = getOtherFaceIdx(edge,currFaceIdx,mesh)

    if otherFace != None:
      faceCenter = mesh.Faces.GetFaceCenter(otherFace) #Point3d
      if getDistanceToEdge(mesh,edge,faceCenter)<=self.tabWidth:
        faceCenter.Transform(xForm)
        self.tabFaceCenter = faceCenter
      else:
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

        """
        color = (0,0,0,0)
        drawVector(vecI,posVecI,color)
        drawVector(vecJ,posVecCenter,color)
        strI = str(angleI)
        strJ = str(angleJ)
        rs.AddTextDot(strI,posVecI)
        rs.AddTextDot(strJ,posVecJ)
        print #wtf: for some reason needed this line to print below
        print( 'angleI: %.2f, angleJ: %.2f' %(angleI,angleJ) )
        """
    elif otherFace==-1:
      print "was nakedEdge"
    else:
      print "otherFace: ",
      print otherFace

  '''ADJACENCY LOOKUP''' #fuckkkk: need to implement some better mesh data structure :(:(

  def getNeighborFlatEdge(self,net):
    '''
    get a neighbor flatEdge
    '''
    verts = self.getNetVerts()
    flatFace = net.flatFaces[self.fromFace]
    flatEdges = flatFace.flatEdges
    flatEdges.remove(self)
    for flatEdge in flatEdges:
      if flatEdge.I in verts or flatEdge.J in verts:
        return flatEdge

  def getOppositeFlatEdge(self,net,flatFace):
    '''
    get the opposite flatEdge (ONLY QUADS!)
    for the given face (fold edges have two faces)
    '''
    verts = self.getNetVerts()
    flatEdges = copy.copy(flatFace.flatEdges)
    flatEdges.remove(self)
    #assert(len(flatEdges)<4), "getOppositeFlatEdge only works for quad faces; face " + str(self.fromFace)+ " is a triangle"
    for flatEdge in flatEdges:
      if flatEdge.I not in verts and flatEdge.J not in verts:
        return flatEdge
    print "Possibly a triangular face: could not find opposite flatEdge for face: " + str(self.fromFace)
    return -1

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

'''FLAT EDGE TESTS'''

def test_FlatEdge():
  '''
  test functionality of various FlatEdge functions
  '''
  vertA = FlatVert(0,Rhino.Geometry.Point3f(5,0,0))
  vertB = FlatVert(1,Rhino.Geometry.Point3f(6,0,0))
  vertC = FlatVert(2,Rhino.Geometry.Point3f(7,10,0))
  flatVerts = [vertA,vertB,vertC]
  angle = math.pi/6.0

  flatEdgeA = FlatEdge(0,0,1)
  flatEdgeA.tabFaceCenter = Rhino.Geometry.Point3d(5,-5,0)

  flatEdgeB = FlatEdge(0,1,2)
  flatEdgeB.tabFaceCenter = Rhino.Geometry.Point3d(5,-5,0)

  '''tests'''
  flatEdgeA._drawEdgeLineNoMesh((0,0,0,0),flatVerts)
  flatEdgeA._drawAngleTab(flatVerts,angle)

  flatEdgeB._drawEdgeLineNoMesh((0,0,0,0),flatVerts)
  flatEdgeB._drawAngleTab(flatVerts,angle)

class FlatFace():
  #does not store meshFace because position in list determines this
  def __init__(self,_vertices,_fromFace,_faceIdx):
    self.vertices = _vertices # a list of netVerts in consistant order (CW or CCW)
    self.flatEdges = []
    self.faceIdx = _faceIdx
    self.fromFace = _fromFace #face adacent to this face which preceded this face in layout
    self.centerPoint = None

    self.polyline = None
    self.geom = [] #each geomElement is a tuple (geom,geom_id)

  '''GET PROPERTIES'''

  def getFlatVerts(self,flatVerts):
    collection = []
    for vert in self.vertices:
      collection.append(flatVerts[vert])
    return collection

  def getFlatVertForTVert(self,tVert,flatVerts):
    assert(tVert in self.vertices.keys())
    return flatVerts[tVert][self.vertices[tVert]]

  def _getCutEdgesSet(self):
    cutEdges = set()
    for flatEdge in self.flatEdges:
      if flatEdge.type == 'cut':
        cutEdges.update([flatEdge])
    return cutEdges

  def _getFoldEdgeSet(self):
    foldEdges = set()
    for flatEdge in self.flatEdges:
      if flatEdge.type == 'fold':
        foldEdges.update([flatEdge])
    return foldEdges

  def getCenterPoint(self,flatVerts,getNew=False):
    if getNew:
      self.centerPoint=None
    if self.centerPoint==None:
      flatVerts = self.getFlatVerts(flatVerts)
      nVerts = len(self.vertices)
      sumX = 0.0
      sumY = 0.0
      for flatVert in flatVerts:
        point = flatVert.point
        sumX += point.X
        sumY += point.Y
      x = sumX/nVerts
      y = sumY/nVerts
      self.centerPoint = Rhino.Geometry.Point3d(x,y,0.0)
    return self.centerPoint

  def getPolylineCurve(self,flatVerts):
    polyline = self.getPolyline(flatVerts)
    return Rhino.Geometry.PolylineCurve(polyline)

  def getPolyline(self,flatVerts):
    points = [flatVerts[i].point for i in self.vertices]
    #add first vert to end to make closed
    points.append(flatVerts[self.vertices[0]].point) 
    return Rhino.Geometry.Polyline(points)

  def getProps(self,flatVerts):
    polylineCurve = self.getPolylineCurve(flatVerts)
    return Rhino.Geometry.AreaMassProperties.Compute(polylineCurve)
  
  def getArea(self,flatVerts):
    props = self.getProps(flatVerts)
    return props.Area

  def getInnerPoint(self,flatVerts,vert):
    cornerVec = Rhino.Geometry.Vector3d(flatVerts[vert].point)
    vec = Rhino.Geometry.Vector3d(centerVec-cornerVec)
    length = vec.Length
    if not vec.Unitize(): return
    vec = vec.Multiply(vec,length*ratio)
    pos = Rhino.Geometry.Vector3d.Add(cornerVec,vec)
    rs.AddTextDot(str(i),pos)

  '''DRAWING'''
  def clearAllGeom(self):
    '''
    delete all geom saved in self.geom
    '''
    if len(self.geom)>0:
      rs.DeleteObjects(self.geom)

  def _addGeom(self,guid):
    assert(str(type(guid))== "<type 'Guid'>"), "attempt to added not guid geom"
    self.geom.append(guid)

  def drawNetFace(self,net):
    '''
    HIGHEST level face drawing
    '''
    flatVerts = net.flatVerts
    polyline = self.getPolyline(flatVerts)
    #remove 'EndArrowhead' to stop displaying orientation of face
    '''
    poly_id,polyline = drawPolyline(polyline,[0,0,0,0],'EndArrowhead')
    self.poly_id = poly_id
    self.polyline = polyline
    #self.geom.append(poly_id)
    self._addGeom(poly_id)
    '''

    #self._drawBuckleFace(net)
    self._drawBuckleFaceAlongFold(net)

  def _drawBuckleFace(self,net):
    '''
    assumes that offset on edge have already been created
    DRAWS PERPEDNDICULAR TO FOLD DIRECITON
    '''
    cutEdgesSet = self._getCutEdgesSet()
    for cutEdge in cutEdgesSet:
      oppositeEdge = cutEdge.getOppositeFlatEdge(net,self)
      if oppositeEdge.type == 'cut' or oppositeEdge.type == 'naked':
        # lineA = cutEdge.getOffsetCorrectOrientation()
        # lineB = oppositeEdge.getOffsetCorrectOrientation()

        lineA = cutEdge.offsetLine
        lineB = oppositeEdge.offsetLine
        self._drawOffsetFaceFromTwoLines(lineA,lineB) #w
        return
    return

  def _drawBuckleFaceAlongFold(self,net):
    '''
    assumes that offset on edge have already been created
    DRAWS ALONG TO FOLD DIRECITON
    '''
    foldEdgeSet = self._getFoldEdgeSet()
    assert(len(foldEdgeSet)>=1), "no fold edges for this face!"
    for foldEdge in foldEdgeSet:
      oppositeEdge = foldEdge.getOppositeFlatEdge(net,self)
      #if oppositeEdge.type == 'fold' or oppositeEdge.type == 'naked':
      xFormA,lineA,lineGuidA = foldEdge._getOffsetEdgeLine(net,self,True)
      xFormB,lineB,lineGuidB = oppositeEdge._getOffsetEdgeLine(net,self,True)
      return self._drawOffsetFaceFromTwoLines(lineA,lineB)
    #if face only has one fold edge:
    if len(foldEdgeSet)==1:
      foldEdge = foldEdgeSet[0]
      oppositeEdge = foldEdge.getOppositeFlatEdge(net,self)
      lineA,lineB = foldEdge.offsetLine,oppositeEdge.offsetLine


  def _drawOffsetFaceFromTwoLines(self,lineA,lineB):
    '''
    assumes CW face winding
    '''
    #  A.To     B.To
    #   |        |  
    #   |        |
    #  A.From   B.From

    diagLineA = Rhino.Geometry.Line(lineA.From,lineB.To)
    diagLineB = Rhino.Geometry.Line(lineB.From,lineA.To)
    intersection = checkIfIntersecting(diagLineA,diagLineB)
    if intersection:
      points = [lineA.From,lineA.To,lineB.To,lineB.From,lineA.From]
    else:
      points = [lineA.From,lineA.To,lineB.From,lineB.To,lineA.From]
    polylineCurve = getPolylineCurve(points)
    curve_id,polylineCurve = drawCurve(polylineCurve)
    #self.geom.append(curve_id)
    self._addGeom(curve_id)
    return curve_id

  def drawInnerface(self,flatVerts,ratio=.33):
    #TODO: UNfinished function
    '''draw a inset face'''
    self.getCenterPoint(flatVerts)
    centerVec = Rhino.Geometry.Vector3d(self.centerPoint)
    for i in range(len(self.vertices)):
      vert = self.vertices[i]
      self.getInnerPoint(flatVerts,vert)
      #TODO: finish up this function
  
  '''TRANSLATION'''
  def translate(self,xForm):
    pass



  '''SEGMENTATION'''

  def resetFlatEdges(self,newFlatEdge):
    '''
    when a new edge is created (bescause of segmentation), the flatEdges that the face which that edge belongs to
    is updated: the old edge is removed and the new edge is inserted
    '''
    edgeIdx = newFlatEdge.edgeIdx
    for flatEdge in self.flatEdges:
      if flatEdge.edgeIdx==edgeIdx:
        self.flatEdges.remove(flatEdge)
        self.flatEdges.append(newFlatEdge)


if __name__=="__main__":
  test_FlatEdge()





  
