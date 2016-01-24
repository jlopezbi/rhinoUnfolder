from visualization import *
import math


class FlatEdge():
    """
    A FlatEdge is an edge of the net.
    It knows what kind of edge it is,
    who its vertices are and where those vertices are
    """

    def __init__(self, edgeIdx, vertI, vertJ):
        self.edgeIdx = edgeIdx
        self.I = vertI
        self.J = vertJ

        self.line = None
        self.line_id = None
        self.geom = []
        self.type = None
        # faces have direct mapping (this is netFace and meshFace)
        self.fromFace = None
        self.toFace = None
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

    def reset(self, oldVert, newVert):
        if self.I == oldVert:
            self.I = newVert
        elif self.J == oldVert:
            self.J = newVert
        else:
            assert(False == True), "error, flatEdge does not have oldVert"

    def getCoordinates(self, flatVerts):
        vertI, vertJ = self.getFlatVerts(flatVerts)
        return [vertI.point, vertJ.point]

    def getFlatVerts(self, flatVerts):
        flatVertI = flatVerts[self.I]
        flatVertJ = flatVerts[self.J]
        return (flatVertI, flatVertJ)

    def getFlatFace(self, flatFaces):
        return flatFaces[self.fromFace]

    def getNetVerts(self):
        return (self.I, self.J)

    def getTVerts(self, mesh):
        return getTVertsForEdge(mesh, self.edgeIdx)

    def getMeshAngle(self, mesh):
        '''get angle of the corresponding mesh edge'''
        if self.angle is None:
            edge = self.edgeIdx
            faceIdxs = getFacesForEdge(mesh, edge)
            if (len(faceIdxs) == 2):
                faceNorm0 = mesh.FaceNormals.Item[faceIdxs[0]]
                faceNorm1 = mesh.FaceNormals.Item[faceIdxs[1]]
                self.angle = Rhino.Geometry.Vector3d.VectorAngle(
                    faceNorm0, faceNorm1)
                return self.angle
            else:
                return None
        else:
            return self.angle

    '''DRAWING'''

    def drawEdgeLine(self, flatVerts, angleThresh, mesh):
        if self.type is not None:
            if self.type == 'fold':
                if self.getMeshAngle(mesh) >= angleThresh:
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
        pointI = flatVerts[self.I].point
        pointJ = flatVerts[self.J].point
        return Rhino.Geometry.Vector3d(pointJ - pointI)

    def resetFromFace(self, face):
        if self.fromFace == face:
            self.fromFace = self.toFace

    def translateGeom(self, movedNetVerts, flatVerts, xForm):
        # self.translateEdgeLine(xForm)
        self.translateNetVerts(movedNetVerts, flatVerts, xForm)
        if self.tabFaceCenter is not None:
            self.tabFaceCenter.Transform(xForm)

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

    '''JOINERY'''

    def drawTab(self, flatVerts):
        '''outputs guid for polyline'''
        if len(self.geom) > 0:
            for guid in self.geom:
                scriptcontext.doc.Objects.Delete(guid, True)
        if len(self.tabAngles) < 1:
            return self.drawTruncatedTab(flatVerts)
            # return self.drawTriTab(net)
        else:
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
                points = [I, intersectPntJ, intersectPntI, J]
            elif shorterThanTab == 0:
                point = [I, K, J]
            elif shorterThanTab == -1:
                points = [
                    I,
                    intersectPntI,
                    intersectPntJ,
                    J]  # order is as expected

            lineA = Rhino.Geometry.Line(I, intersectPntI)
            lineB = Rhino.Geometry.Line(J, intersectPntJ)

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

    def getConnectToFace(self, flatFaces, mesh):
        return flatFaces[getOtherFaceIdx(self.edgeIdx, self.fromFace, mesh)]

    def drawFaceHole(self, net, holeRadius):
        pntA, pntC = self.getCoordinates(net.flatVerts)
        pntB = net.flatFaces[self.fromFace].getCenterPoint(net.flatVerts, True)
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

    def circleIsInFace(self, net, circle):
        # faceForEdge =
        # faceBoundary = net.
        pass

    def getHolePoints(self, flatVerts):
        # TODO: replace this with less redundant version (iterate trhough
        # points)
        pointI, pointJ = (None, None)
        if self.distI != -1:
            vecI = self.getEdgeVec(flatVerts)
            vecI.Unitize()
            vecI = vecI * self.distI
            pointI = (flatVerts[self.I].point + vecI)
            pointI = pointI + self.holeVec
        if self.distJ != -1:
            vecJ = -1 * self.getEdgeVec(flatVerts)
            vecJ.Unitize()
            vecJ = vecJ * self.distJ
            pointJ = (flatVerts[self.J].point + vecJ)
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

    def clearAllGeom(self):
        '''
        note: clear self.geom and self.line_id ?
        '''
        if self.line_id is not None:
            scriptcontext.doc.Objects.Delete(self.line_id, True)
            self.line_id = None

        if len(self.geom) > 0:
            for guid in self.geom:
                scriptcontext.doc.Objects.Delete(guid, True)

    def getMidPoint(self, flatVerts):
        coordinates = self.getCoordinates(flatVerts)
        pntA = coordinates[0]
        pntB = coordinates[1]
        x = (pntA.X + pntB.X) / 2.0
        y = (pntA.Y + pntB.Y) / 2.0
        z = (pntA.Z + pntB.Z) / 2.0
        return Rhino.Geometry.Point3f(x, y, z)

    def getFaceFromPoint(self, net, point):
        '''return the face that corresponds to the point
        '''
        # TODO: fails for horizontal lines :(
        assert(self.type == 'fold')
        faceA = self.fromFace
        faceB = self.toFace
        leftA = self.testFacesIsLeft(net, faceA)
        leftB = self.testFacesIsLeft(net, faceB)
        assert(leftA != leftB), "both faces found to be on same side of edge"
        leftPoint = self.testPointIsLeft(point, net.flatVerts)
        if leftA == leftPoint:
            return faceA
        elif leftB == leftPoint:
            return faceB
        print "unable to find face"
        return

    def testFacesIsLeft(self, net, face):
        '''find which side the face is on relative to this edge
        ouput: 1 for left, -1 for right, 0 for error
        '''

        testPoint = net.flatVerts[self.getNeighborFlatVert(net, face)].point
        if not testPoint:
            return -1
        return self.testPointIsLeft(testPoint, net.flatVerts)

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
        tVertsEdge = set([self.I, self.J])
        flatFace = net.flatFaces[face]
        tVertsFace = set(flatFace.vertices)
        neighbors = list(tVertsFace - tVertsEdge)
        return neighbors[0]  # arbitrarily return first tVert

    def getEdgeLine(self, flatVerts):
        pntI, pntJ = self.getCoordinates(flatVerts)
        return Rhino.Geometry.Line(pntI, pntJ)

    def getTabFaceCenter(self, mesh, currFace, xForm):
        otherFace = getOtherFaceIdx(self.edgeIdx, currFace, mesh)
        if otherFace is not None and otherFace != -1:
            faceCenter = mesh.Faces.GetFaceCenter(otherFace)
            faceCenter.Transform(xForm)
            faceCenter.Z = 0.0  # this results in small error, TODO: change to more robust method
            self.tabFaceCenter = faceCenter
        if self.tabFaceCenter is None:
            return False
        else:
            return True

    def getTabAngles(self, mesh, currFaceIdx, xForm):
        # WORKING AWAY FROM THIS: data is implicit in
        edge = self.edgeIdx
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
