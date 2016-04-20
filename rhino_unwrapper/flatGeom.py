from visualization import *
import rhinoscriptsyntax as rs
import Rhino.Geometry as geom
import math


class FlatVert():

    def __init__(self, point, tVertIdx=None,fromFace=None):
        self.point = point
        self.tVertIdx = tVertIdx
        self.fromFace = fromFace
        self.edgeIdx = None
        #self.toFace = None
        self.geom = []
        self.color = {'magenta':(255,0,255)}

    @classmethod
    def from_coordinates(cls,x,y,z):
        point = geom.Point3d(x,y,z)
        return cls(point)

    def display(self,index=None):
        rs.AddPoint(self.point)
        if index!=None:
            dot_guid = rs.AddTextDot(str(index),self.point)
            rs.ObjectColor(dot_guid,self.color['magenta'])

    def hasSamePoint(self, point):
        return approxEqual(self.point.X, point.X) and approxEqual(
            self.point.Y, point.Y)

    def translate(self, xForm):
        self.point.Transform(xForm)


class FlatFace():

    def __init__(self, vertices,edges):
        self.vertices = vertices  # a list of netVerts
        self.edges = edges #ccw with face normal
        self.centerPoint = None

    def get_normal(self,verts=None):
        ''' For now returns unit z vector '''
        return geom.Vector3d(0.0,0.0,1.0)
    
    def getFlatVerts(self, flatVerts):
        collection = []
        for vert in self.vertices:
            collection.append(flatVerts[vert])
        return collection

    def getFlatVertForTVert(self, tVert, flatVerts):
        assert(tVert in self.vertices.keys())
        return flatVerts[tVert][self.vertices[tVert]]

    def getCenterPoint(self, flatVerts, getNew=False):
        """
        assumes face is in XY Plane!
        """
        if getNew:
            self.centerPoint = None
        if self.centerPoint is None:
            flatVerts = self.getFlatVerts(flatVerts)
            nVerts = len(self.vertices)
            sumX = 0.0
            sumY = 0.0
            for flatVert in flatVerts:
                point = flatVert.point
                sumX += point.X
                sumY += point.Y
            x = sumX / nVerts
            y = sumY / nVerts
            self.centerPoint = Rhino.Geometry.Point3d(x, y, 0.0)
        return self.centerPoint

    def draw(self, flatVerts):
        polyline = self.getPolyline(flatVerts)
        # remove 'EndArrowhead' to stop displaying orientatio of face
        poly_id = drawPolyline(polyline, arrowType='end')
        self.poly_id = poly_id
        self.polyline = polyline

    def getPolyline(self, flatVerts):
        points = [flatVerts[i].point for i in self.vertices]
        # add first vert to end to make closed
        points.append(flatVerts[self.vertices[0]].point)
        return Rhino.Geometry.Polyline(points)

    def getPolylineCurve(self, flatVerts):
        polyline = self.getPolyline(flatVerts)
        return Rhino.Geometry.PolylineCurve(polyline)

    def getProps(self, flatVerts):
        polylineCurve = self.getPolylineCurve(flatVerts)
        return Rhino.Geometry.AreaMassProperties.Compute(polylineCurve)

    def getArea(self, flatVerts):
        props = self.getProps(flatVerts)
        return props.Area

    def drawInnerface(self, flatVerts, ratio=.33):
        '''draw a inset face'''
        self.getCenterPoint(flatVerts)
        centerVec = Rhino.Geometry.Vector3d(self.centerPoint)
        for i in range(len(self.vertices)):
            vert = self.vertices[i]
            self.getInnerPoint(flatVerts, vert)
            # TODO: finish up this function

    def getInnerPoint(self, flatVerts, vert):
        cornerVec = Rhino.Geometry.Vector3d(flatVerts[vert].point)
        vec = Rhino.Geometry.Vector3d(centerVec - cornerVec)
        length = vec.Length
        if not vec.Unitize():
            return
        vec = vec.Multiply(vec, length * ratio)
        pos = Rhino.Geometry.Vector3d.Add(cornerVec, vec)
        rs.AddTextDot(str(i), pos)
