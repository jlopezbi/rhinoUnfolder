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

    def display(self,group_name):
        point_guid = rs.AddPoint(self.point)
        rs.AddObjectToGroup(point_guid,group_name)

    def display_index(self,group_name,index):
        dot_guid = rs.AddTextDot(str(index),self.point)
        rs.ObjectColor(dot_guid,self.color['magenta'])
        rs.AddObjectToGroup(dot_guid,group_name)


    def same_coordinates(self,x,y,z):
        point = geom.Point3d(x,y,z)
        return self.hasSamePoint(point)

    def hasSamePoint(self, point):
        return self.point.Equals(point)

    def translate(self, xForm):
        self.point.Transform(xForm)


class FlatFace():

    def __init__(self, vertices,edges):
        self.vertices = vertices  #ORDERED a list of netVerts
        self.edges = edges #ORDERED ccw with face normal
        self.centerPoint = None

    def get_normal(self,verts=None):
        ''' For now returns unit z vector '''
        return geom.Vector3d(0.0,0.0,1.0)
    
    def getFlatVerts(self, island):
        collection = []
        for vert in self.vertices:
            collection.append(island.flatVerts[vert])
        return collection

    def get_points(self,island):
        points = []
        for vert in self.vertices:
            points.append(island.flatVerts[vert].point)
        return points
    
    def getFlatVertForTVert(self, tVert, flatVerts):
        assert(tVert in self.vertices.keys())
        return flatVerts[tVert][self.vertices[tVert]]

    def getCenterPoint(self, island, getNew=False):
        """
        NOTE: could probably also get center from polyline
        """

        if getNew:
            self.centerPoint = None
        if self.centerPoint is None:
            sumX = 0.0
            sumY = 0.0
            sumZ = 0.0
            for vert in self.vertices:
                point = island.get_point_for_vert(vert)
                sumX += point.X
                sumY += point.Y
                sumZ += point.Z
            nVerts = len(self.vertices)
            x = sumX / nVerts
            y = sumY / nVerts
            z = sumZ / nVerts
            self.centerPoint = geom.Point3d(x,y,z)
        return self.centerPoint

    def draw(self, island):
        polyline = self.getPolyline(island)
        # remove 'EndArrowhead' to stop displaying orientatio of face
        poly_id = drawPolyline(polyline, arrowType='end')
        self.poly_id = poly_id
        self.polyline = polyline
        rs.AddObjectToGroup(poly_id,island.group_name)

    def show_index(self,index,island):
        point = self.getCenterPoint(island)
        dot_id = rs.AddTextDot(str(index),point)
        rs.AddObjectToGroup(dot_id,island.group_name)

    def getPolyline(self, island):
        points = [island.flatVerts[i].point for i in self.vertices]
        # add first vert to end to make closed
        points.append(island.flatVerts[self.vertices[0]].point)
        return Rhino.Geometry.Polyline(points)

    def getPolylineCurve(self, island):
        polyline = self.getPolyline(island)
        return Rhino.Geometry.PolylineCurve(polyline)

    def getProps(self, island):
        polylineCurve = self.getPolylineCurve(island)
        return Rhino.Geometry.AreaMassProperties.Compute(polylineCurve)

    def getArea(self, island):
        props = self.getProps(island)
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
