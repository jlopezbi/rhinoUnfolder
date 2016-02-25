from visualization import * 
import math 

def change_to_cut_edge(flatEdge,otherEdgeIdx):
    newEdge = CutEdge(meshEdgeIdx = flatEdge.meshEdgeIdx,
                      vertAidx = flatEdge.vertAidx,
                      vertBidx = flatEdge.vertBidx,
                      fromFace = flatEdge.fromFace,
                      toFace = flatEdge.toFace,
                      sibling = otherEdgeIdx)
    return newEdge

class FlatEdge(object):
    def __init__(self,**kwargs):
        self.meshEdgeIdx = kwargs['meshEdgeIdx']
        self.vertAidx = kwargs['vertAidx']
        self.vertBidx = kwargs['vertBidx']
        self.fromFace = kwargs['fromFace']
        self.toFace = kwargs.get('toFace',None)
        self.color = kwargs.get('color',(0,0,0,0))
        self.line = None
        self.line_id = None
        self.geom = []
        self.post_initialize(kwargs)

    def post_initialize(self,kwargs):
        pass

    def show(self,flatVerts):
        pass

    def show_line(self,flatVerts):
        points = self.getCoordinates(flatVerts)
        if self.line_id is not None:
            scriptcontext.doc.Objects.Delete(self.line_id, True)
        line_id, line = drawLine(points, self.color, 'None')
        self.line_id = line_id
        self.line = line
        return line_id

    def type(self):
        #TODO: find better way
        return 'FlatEdge'

    def reset(self, oldVert, newVert):
        if self.vertAidx == oldVert:
            self.vertAidx = newVert
        elif self.vertBidx == oldVert:
            self.vertBidx = newVert
        else:
            assert(False == True), "error, flatEdge does not have oldVert"

    def getCoordinates(self, flatVerts):
        vertI, vertJ = self.getFlatVerts(flatVerts)
        return (vertI.point, vertJ.point)

    def getFlatVerts(self, flatVerts):
        flatVertI = flatVerts[self.vertAidx]
        flatVertJ = flatVerts[self.vertBidx]
        return (flatVertI, flatVertJ)

    def getFlatFace(self, flatFaces):
        return flatFaces[self.fromFace]

    def getEdgeLine(self, flatVerts):
        pntI, pntJ = self.getCoordinates(flatVerts)
        return Rhino.Geometry.Line(pntI, pntJ)

    def getNetVerts(self):
        return (self.vertAidx, self.vertBidx)

    def getTVerts(self, mesh):
        return getTVertsForEdge(mesh, self.meshEdgeIdx)

    def getMeshAngle(self, myMesh):
        '''get dihedral angle of the corresponding mesh edge'''
        if self.angle is None:
            self.angle = myMesh.getEdgeAngle(self.meshEdgeIdx)
            return self.angle
        else:
            return self.angle

    def get_other_face_center(self, myMesh, currFace, xForm):
        # NOTE appears to be failing for orthogonal geom
        # NOTE perhaps should be a method only CutEdge implements?
        '''
        This function works in the context of layout, where xForms are being
        created
        '''
        otherFace = myMesh.getOtherFaceIdx(self.meshEdgeIdx, currFace)
        if otherFace is not None and otherFace != -1:
            faceCenter = myMesh.mesh.Faces.GetFaceCenter(otherFace)
            faceCenter.Transform(xForm)
            faceCenter.Z = 0.0  # this results in small error, TODO: change to more robust method
            self.tabFaceCenter = faceCenter
        if self.tabFaceCenter is None:
            return False
        else:
            return True

    def drawEdgeLine(self, flatVerts, angleThresh, myMesh):
        # DEPRICATED Legacy code
        if self.type is not None:
            if self.type == 'fold':
                if self.getMeshAngle(myMesh) >= angleThresh:
                    color = (0, 49, 224, 61)  # green
                else:
                    # bluegreyish for no crease lines
                    color = (0, 161, 176, 181)
            elif self.type == 'cut':
                color = (0, 237, 43, 120)  # red
                if self.hasTab:
                    color = (0, 255, 0, 255)  # magenta
                    self.drawTab(flatVerts)
            elif self.type == 'naked':
                color = (0, 55, 156, 196)  # blue
            points = self.getCoordinates(flatVerts)
            if self.line_id is not None:
                scriptcontext.doc.Objects.Delete(self.line_id, True)
            # EndArrowhead StartArrowhead
            line_id, line = drawLine(points, color, 'None')
            self.line_id = line_id
            self.line = line
        return line_id

    def getEdgeVec(self, flatVerts):
        pointI = flatVerts[self.vertAidx].point
        pointJ = flatVerts[self.vertBidx].point
        return Rhino.Geometry.Vector3d(pointJ - pointI)

    def resetFromFace(self, face):
        if self.fromFace == face:
            self.fromFace = self.toFace
            self.toFace = face
            
    def getOtherFace(self,face):
        if self.fromFace == face:
            return self.toFace
        elif self.toFace == face:
            return self.fromFace
        else:
            return None

    def getConnectToFace(self, flatFaces, mesh):
        return flatFaces[getOtherFaceIdx(self.meshEdgeIdx, self.fromFace, mesh)]

    def getMidPoint(self, flatVerts):
        coordinates = self.getCoordinates(flatVerts)
        pntA = coordinates[0]
        pntB = coordinates[1]
        x = (pntA.X + pntB.X) / 2.0
        y = (pntA.Y + pntB.Y) / 2.0
        z = (pntA.Z + pntB.Z) / 2.0
        return Rhino.Geometry.Point3f(x, y, z)

    def getFaceFromPoint(self,flatFaces,flatVerts,point):
        """
        the given point is assumed to be on one side of the edge or another.
        If colinear return None
        Otherwise return the face that is on the same side as the point
        """
        pntI,pntJ = self.getCoordinates(flatVerts)
        selfVec = self.getEdgeVec(flatVerts)
        pntVec = Rhino.Geometry.Vector3d(point - pntI)
        faceA = flatFaces[self.fromFace]
        faceB = flatFaces[self.toFace]
        faceCenterA = faceA.getCenterPoint(flatVerts)
        faceCenterB = faceB.getCenterPoint(flatVerts)
        faceVecA = Rhino.Geometry.Vector3d(faceCenterA-pntI)
        faceVecB = Rhino.Geometry.Vector3d(faceCenterB-pntI)
        selfxPnt = Rhino.Geometry.Vector3d.CrossProduct(selfVec,pntVec) 
        if selfxPnt.IsZero:
            print "Point was coincident with flatEdge"
            return None
        selfxFaceA = Rhino.Geometry.Vector3d.CrossProduct(selfVec,faceVecA)
        selfxFaceB = Rhino.Geometry.Vector3d.CrossProduct(selfVec,faceVecB)
        def sign(x): return x/math.fabs(x)
        if sign(selfxFaceA.Z) == sign(selfxFaceB.Z):
            print "both faces on same side of edge, or both have centers coincident with edge"
            return None
        if sign(selfxPnt.Z) == sign(selfxFaceA.Z):
            return self.fromFace
        elif sign(selfxPnt.Z):
            return self.toFace
        else:
            "some unforseen problem in FlatEdge.getFaceFromPoint"
            return None


    def testFacesIsLeft(self, net, face):
        '''find which side the face is on relative to this edge
        ouput: 1 for left, -1 for right, 0 for error
        '''

        testPoint = net.flatVerts[self.getNeighborFlatVert(net, face)].point
        if not testPoint:
            return -1
        return self.testPointIsLeft(testPoint, net.flatVerts)

    

    def testPointIsLeft(self, testPoint, flatVerts):
        '''
        use cross product to see if testPoint is to the left of
        the edgLine
        returns False if co-linear. HOwever, if the mesh is triangulated
        and has no zero-area faces this should not occur.
        '''
        pntA, pntB = self.getCoordinates(flatVerts)
        vecLine = getVectorForPoints(pntA, pntB)
        vecTest = getVectorForPoints(pntA, testPoint)  # this may be too skewed
        cross = Rhino.Geometry.Vector3d.CrossProduct(vecLine, vecTest)
        z = cross.Z  # (pos and neg)
        return z > 0

    def getNeighborFlatVert(self, net, face=None):
        '''
        gets one of the flatVerts associated with the given
        face, but that is not a part of this flatEdge.
        if face==None uses the fromFace associated with this edge
        '''

        if face is None:
            face = self.fromFace
        tVertsEdge = set([self.vertAidx, self.vertBidx])
        flatFace = net.flatFaces[face]
        tVertsFace = set(flatFace.vertices)
        neighbors = list(tVertsFace - tVertsEdge)
        return neighbors[0]  # arbitrarily return first tVert

    def getFacePoint(self, flatVerts, flatFaces):
        return flatFaces[self.fromFace].getCenterPoint(flatVerts)

    def getFacePolyline(self, net):
        polylineCurve = net.flatFaces[
            self.fromFace].getPolylineCurve(
            net.flatVerts)
        return polylineCurve

    def inFace(self, net, point):
        polylineCurve = self.getFacePolyline(net)
        relationship = polylineCurve.Contains(point)
        if Rhino.Geometry.PointContainment.Unset == relationship:
            print "curve was not closed, relationship meaningless"
            return
        elif Rhino.Geometry.PointContainment.Inside == relationship:
            return True
        elif Rhino.Geometry.PointContainment.Outside == relationship:
            return False
        else:
            # coincident, still leads to bad condition for holes
            return False


    '''
    TRANSLATION STUFF
    '''
    def translateGeom(self, movedNetVerts, flatVerts, xForm):
        # self.translateEdgeLine(xForm)
        self.translateNetVerts(movedNetVerts, flatVerts, xForm)
        if self.geom:
            for element in self.geom:
                element.Transform(xForm)

    def translateEdgeLine(self, xForm):
        if self.line is not None:
            self.line.Transform(xForm)
            scriptcontext.doc.Objects.Replace(self.line_id, self.line)

    def translateNetVerts(self, movedNetVerts, flatVerts, xForm):
        netVertI, netVertJ = self.getFlatVerts(flatVerts)
        if netVertI not in movedNetVerts:
            netVertI.translate(xForm)
            movedNetVerts.append(netVertI)
        if netVertJ not in movedNetVerts:
            netVertJ.translate(xForm)
            movedNetVerts.append(netVertJ)

    def clearAllGeom(self):
        '''
        note: clear self.geom and self.line_id ?
        '''
        if self.line_id is not None:
            scriptcontext.doc.Objects.Delete(self.line_id, True)
            self.line_id = None

        if self.geom:
            for guid in self.geom:
                scriptcontext.doc.Objects.Delete(guid, True)

class FoldEdge(FlatEdge):
    
    def post_initialize(self,kwargs):
        pass
    
    def show(self,flatVerts):
        self._show_crease(flatVerts)

    def _show_crease(self,flatVerts):
        pass

    def type(self):
        # TODO: find better way
        return 'FoldEdge'

class CutEdge(FlatEdge):

    def post_initialize(self,kwargs):
        self.sibling = kwargs['sibling']

    def show(self,flatVerts):
        self._show_joinery(flatVerts)
    
    def _show_joinery(self,flatVerts):
        pass

    def type(self):
        # TODO: find better way
        return 'CutEdge'

    def setTabSide(self, facePoint, flatVerts):
        '''
        occurs affter complete layout
        '''
        if self.tabOnLeft is None:
            #testPoint = net.flatVerts[self.getNeighborFlatVert(net)].point
            if self.testPointIsLeft(facePoint, flatVerts):
                self.tabOnLeft = False
            else:
                self.tabOnLeft = True
            return self.tabOnLeft
        else:
            return self.tabOnLeft

    def drawTab(self, flatVerts):
        '''outputs guid for polyline'''
        if len(self.geom) > 0:
            for guid in self.geom:
                scriptcontext.doc.Objects.Delete(guid, True)
        if len(self.tabAngles) < 1:
            return self.drawTruncatedTab(flatVerts)
        else:
            print "quadtab"
            return self.drawQuadTab(flatVerts)

    def drawQuadTab(self, flatVerts):
        pntA, pntD = self.getCoordinates(flatVerts)
        vecA = Rhino.Geometry.Vector3d(pntA)
        vecD = Rhino.Geometry.Vector3d(pntD)

        alpha = self.tabAngles[0]
        beta = self.tabAngles[1]

        lenI = self.tabWidth / math.sin(alpha * math.pi / 180.0)
        lenJ = self.tabWidth / math.sin(beta * math.pi / 180.0)

        if not self.tabOnLeft:
            alpha = -1 * alpha
            beta = -1 * beta

        vec = vecD.Subtract(vecD, vecA)
        vecUnit = rs.VectorUnitize(vec)
        vecI = rs.VectorScale(vecUnit, lenI)
        vecJ = rs.VectorScale(vecUnit, -lenJ)

        vecI = rs.VectorRotate(vecI, alpha, [0, 0, 1])
        vecJ = rs.VectorRotate(vecJ, -beta, [0, 0, 1])
        vecB = vecA + vecI
        vecC = vecD + vecJ

        pntB = Rhino.Geometry.Point3d(vecB)
        pntC = Rhino.Geometry.Point3d(vecC)

        points = [pntA, pntB, pntC, pntD]
        polyGuid = rs.AddPolyline(points)

        self.geom.append(polyGuid)
        return polyGuid

    def drawTruncatedTab(self, flatVerts):
        '''
        draw a truncated tab using the drawing style of triTab, but with an offset-line intersection
        '''
        tabLen = self.tabWidth
        I, J = self.getCoordinates(flatVerts)
        K = self.tabFaceCenter
        if self.tabFaceCenter is None:  # this is ahack: TODO: if a new cut edge is created, give it a tabFaceCenter
            return
        diagA = Rhino.Geometry.Line(I, K)
        diagB = Rhino.Geometry.Line(J, K)
        offsetLine, vecA = getOffset((I, J), K, tabLen, True)

        resultI, aI, bI = Rhino.Geometry.Intersect.Intersection.LineLine(
            offsetLine, diagA)
        resultJ, aJ, bJ = Rhino.Geometry.Intersect.Intersection.LineLine(
            offsetLine, diagB)
        if resultI and resultJ:
            intersectPntI = offsetLine.PointAt(aI)
            intersectPntJ = offsetLine.PointAt(aJ)

            shorterThanTab = self.checkIfShortTab(flatVerts)
            if shorterThanTab == 1:
                # flip order to avoid self-intersction
                points = [I, K, J]
            elif shorterThanTab == 0:
                points = [I, K, J]
            elif shorterThanTab == -1:
                points = [
                    I,
                    intersectPntI,
                    intersectPntJ,
                    J]  # order is as expected
        else:
            points = [I, K, J]

        polyGuid = rs.AddPolyline(points)
        self.geom.append(polyGuid)

        return polyGuid

    def checkIfShortTab(self, flatVerts):
        center = self.tabFaceCenter
        edgeLine = self.getEdgeLine(flatVerts)
        closestPnt = edgeLine.ClosestPoint(center, True)
        vec = Rhino.Geometry.Point3d.Subtract(center, closestPnt)
        lenVec = vec.Length
        if lenVec < self.tabWidth:
            return 1
        if lenVec == self.tabWidth:
            return 0
        else:
            return -1

    def drawTriTab(self, net):
        holeRadius = net.holeRadius
        mesh = net.mesh
        flatVerts = net.flatVerts
        flatFaces = net.flatFaces

        minArea = (holeRadius**2.0) * math.pi * 30
        # print "minArea: " + str(minArea)

        flatFace = self.getConnectToFace(flatFaces, mesh)
        area = flatFace.getArea(flatVerts)

        pntA, pntC = self.getCoordinates(flatVerts)
        pntB = self.tabFaceCenter

        points = [pntA, pntB, pntC]
        polyline = Rhino.Geometry.PolylineCurve([pntA, pntB, pntC, pntA])
        props = Rhino.Geometry.AreaMassProperties.Compute(polyline)
        if area > minArea:
            centerPnt = props.Centroid
        else:
            rs.AddTextDot("o", pntB)
            centerPnt = flatFaces[
                self.fromFace].getCenterPoint(
                flatVerts, True)
        hole = rs.AddCircle(centerPnt, holeRadius)
        polyGuid = rs.AddPolyline(points)
        self.geom.append(polyGuid)
        self.geom.append(hole)
        return polyGuid

    def getTabAngles(self, mesh, currFaceIdx, xForm):
        # WORKING AWAY FROM THIS: data is implicit in tabFace center
        edge = self.meshEdgeIdx
        otherFace = getOtherFaceIdx(edge, currFaceIdx, mesh)

        if otherFace is not None:
            faceCenter = mesh.Faces.GetFaceCenter(otherFace)  # Point3d
            if getDistanceToEdge(mesh, edge, faceCenter) <= self.tabWidth:
                faceCenter.Transform(xForm)
                self.tabFaceCenter = faceCenter
            else:
                posVecCenter = Rhino.Geometry.Vector3d(faceCenter)

                pntI, pntJ = getPointsForEdge(mesh, edge)  # Point3d
                vecEdge = getEdgeVector(mesh, edge)  # Vector3d
                posVecI = Rhino.Geometry.Vector3d(pntI)
                posVecJ = Rhino.Geometry.Vector3d(pntJ)

                vecI = Rhino.Geometry.Vector3d.Subtract(posVecCenter, posVecI)
                vecJ = Rhino.Geometry.Vector3d.Subtract(posVecJ, posVecCenter)

                angleI = rs.VectorAngle(vecI, vecEdge)
                angleJ = rs.VectorAngle(vecJ, vecEdge)

                self.tabAngles = [angleI, angleJ]

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
        elif otherFace == -1:
            print "was nakedEdge"
        else:
            print "otherFace: ",
            print otherFace

    def drawFaceHole(self, flatVerts,flatFaces, holeRadius):
        pntA, pntC = self.getCoordinates(flatVerts)
        pntB = flatFaces[self.fromFace].getCenterPoint(flatVerts, True)
        pnts = [pntA, pntB, pntC, pntA]
        polyline = Rhino.Geometry.PolylineCurve(pnts)
        props = Rhino.Geometry.AreaMassProperties.Compute(polyline)
        centerPnt = props.Centroid
        hole = rs.AddCircle(centerPnt, holeRadius)
        self.geom.append(hole)

    def drawHoles(self, net, connectorDist, safetyRadius, holeRadius):
        self.assignHoleDists(net, connectorDist, safetyRadius)
        points = self.getHolePoints(net.flatVerts)
        safeR = holeRadius + (safetyRadius - holeRadius) / 2.0
        geom = [[0, 0], [0, 0]]
        for i, point in enumerate(points):
            if point is not None:
                geom[i][0] = Rhino.Geometry.Circle(point, holeRadius)
                circleSafe = Rhino.Geometry.Circle(point, safeR)
                geom[i][1] = Rhino.Geometry.ArcCurve(circleSafe)
        if geom[0][0] != 0 and geom[1][0] != 0:
            tolerance = .001
            plane = Rhino.Geometry.Plane(
                Rhino.Geometry.Point3d(
                    0, 0, 0), Rhino.Geometry.Vector3d(
                    0, 0, 1))

            # check if the circles are inside there parent face

            # check if the circles are intersectin each other
            relation = Rhino.Geometry.Curve.PlanarClosedCurveRelationship(
                geom[0][1], geom[1][1], plane, tolerance)
            if relation == Rhino.Geometry.RegionContainment.Disjoint:
                guidI = scriptcontext.doc.Objects.AddCircle(geom[0][0])
                guidJ = scriptcontext.doc.Objects.AddCircle(geom[1][0])

                # draw lines for debugging
                centerPnt = geom[0][0].Center
                rs.AddLine(centerPnt, self.line.ClosestPoint(centerPnt, True))

                centerPnt = geom[1][0].Center
                rs.AddLine(centerPnt, self.line.ClosestPoint(centerPnt, True))

                self.geom.extend((guidI, guidJ))
            elif relation == Rhino.Geometry.RegionContainment.MutualIntersection:
                # only add I circle
                guid = scriptcontext.doc.Objects.AddCircle(geom[0][0])
                self.geom.append(guid)
        elif geom[0][0] != 0:
            guid = scriptcontext.doc.Objects.AddCircle(geom[0][0])
            self.geom.append(guid)
        elif geom[1][0] != 0:
            guid = scriptcontext.doc.Objects.AddCircle(geom[1][0])
            self.geom.append(guid)

    def getHolePoints(self, flatVerts):
        # TODO: replace this with less redundant version (iterate trhough
        # points)
        pointI, pointJ = (None, None)
        if self.distI != -1:
            vecI = self.getEdgeVec(flatVerts)
            vecI.Unitize()
            vecI = vecI * self.distI
            pointI = (flatVerts[self.vertAidx].point + vecI)
            pointI = pointI + self.holeVec
        if self.distJ != -1:
            vecJ = -1 * self.getEdgeVec(flatVerts)
            vecJ.Unitize()
            vecJ = vecJ * self.distJ
            pointJ = (flatVerts[self.vertBidx].point + vecJ)
            pointJ = pointJ + self.holeVec
        return (pointI, pointJ)

    def assignHoleDists(self, net, connectorDist, safetyRadius):
        if self.distI is None and self.distJ is None:
            pair = net.flatEdges[self.pair]
            distsA = pair.getHoleDistances(net, connectorDist, safetyRadius)
            distsB = self.getHoleDistances(net, connectorDist, safetyRadius)
            distI = max(distsA[0], distsB[0])
            distJ = max(distsA[1], distsB[1])

            pair.distI = distI
            pair.distJ = distJ
            pair.holeVec = distsA[2]
            self.distI = distI
            self.distJ = distJ
            self.holeVec = distsB[2]

    def assignHoleDistsRatio(self, flatVerts, ratio):
        edgeVec = self.getEdgeVec(flatVerts)
        length = edgeVec.Length
        distI = length * ratio
        distJ = length * ratio
        return (distI, distJ, vec)

    def getHoleDistancesSimple(self, net, connectorDist, ratioEdgeLen):
        edgeVec = self.getEdgeVec(net.flatVerts)

    def getHoleDistances(self, net, connectorDist, safetyRadius):
        '''
        get the two distances for a given edge by interescting the offset lines
        from the edge line and the two lines formed from the edgePoints to faceCenter
        '''
        flatVerts = net.flatVerts
        flatFaces = net.flatFaces
        # assumes laying-out in xy plane
        axis = Rhino.Geometry.Vector3d(0.0, 0.0, 1.0)
        K = self.getFacePoint(flatVerts, flatFaces)  # CenterPoint
        # rs.AddPoint(K)
        I, J = self.getCoordinates(flatVerts)
        offsetLineA, vecA = getOffset(
            (I, J), K, connectorDist, True)  # EdgeOffset
        offsetLineB, vecB = getOffset((I, K), J, safetyRadius, True)
        offsetLineC, vecC = getOffset((J, K), I, safetyRadius, True)

        rcI, aI, bI = Rhino.Geometry.Intersect.Intersection.LineLine(
            offsetLineA, offsetLineB)
        if not rcI:
            print "No Intersection found for first chordB"
            return Rhino.Commands.Result.Nothing
        rcJ, aJ, bJ = Rhino.Geometry.Intersect.Intersection.LineLine(
            offsetLineA, offsetLineC)
        if not rcJ:
            print "No Intersection found for second chordC"
            return Rhino.Commands.Result.Nothing
        pointI = offsetLineA.PointAt(aI)
        pointJ = offsetLineA.PointAt(aJ)
        # CHECK IF POINTS ARE WITHIN THAT FACE
        if self.line is None:
            self.line = Rhino.Geometry.Line(I, J)

        if not self.inFace(net, pointI):
            print "assining -1"
            distI = -1
        else:
            pntOnEdgeI = self.line.ClosestPoint(pointI, True)
            distI = pntOnEdgeI.DistanceTo(I)

        if not self.inFace(net, pointJ):
            distJ = -1
        else:
            pntOnEdgeJ = self.line.ClosestPoint(pointJ, True)
            distJ = pntOnEdgeJ.DistanceTo(J)
        # rs.AddPoint(pntOnEdgeI)
        # rs.AddPoint(pntOnEdgeJ)
        return (distI, distJ, vecA)  # vecA will be used to place actually hole

class NakedEdge(FlatEdge):

    def post_initialize(self,kwargs):
        pass

class _FlatEdge():
    """
    DEPRICATED
    A FlatEdge is an edge of the net.
    It knows what kind of edge it is,
    who its vertices are and where those vertices are

    EVERY single flat edge shall knowith its from face and two face!
    """

    def __init__(self, edgeIdx, vertI, vertJ,fromFace,toFace=None):
        self.meshEdgeIdx = edgeIdx
        self.vertAidx = vertI
        self.vertBidx = vertJ

        self.line = None
        self.line_id = None
        self.geom = []
        self.type = None
        # faces have direct mapping (this is netFace and meshFace)
        self.fromFace = fromFace
        self.toFace = toFace
        self.angle = None

        '''JOINERY'''
        self.tabOnLeft = None  # important for general joinery drawing

        '''Tabs'''
        self.hasTab = False
        self.tabFaceCenter = None  # point3d
        self.tabAngles = []
        self.tabWidth = .5  # could be standard, or based on face area

        '''Holes'''
        self.distI = None
        self.distJ = None

    
    '''DRAWING'''

    
    '''JOINERY'''

    



    

    

        

    



