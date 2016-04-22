from rhino_helpers import *
import rhino_helpers as helper
import Rhino.Geometry as geom
import visualization 
import math

reload(visualization)

def get_mapped_point(point,from_frame,to_frame):
    did_map, mapped_point = from_frame.plane.RemapToPlaneSpace(point)
    assert did_map, "get_mapped_point failed for point {}".format(point)
    final_point = to_frame.plane.PointAt(mapped_point.X,mapped_point.Y,mapped_point.Z)
    return final_point

def get_frame_on_mesh_implicit(meshLoc,myMesh):
    '''
    an edge and a face (meshLoc) imply a unique frame, since the edge can be oriented according the the face's normal (right hand rule)
    '''
    face,edge = meshLoc
    face_edges = myMesh.getFaceEdges(face)
    assert (edge in face_edges), "edge {} not in face {}".format(edge,face)
    basePoint,endPoint = myMesh.get_oriented_points_for_edge(edge,face)
    normal = myMesh.get_face_normal(face)
    xVec = helper.getVectorForPoints(basePoint,endPoint)
    return Frame.create_frame_from_normal_and_x(basePoint,normal,xVec)

def get_frame_on_mesh(mesh_location,myMesh):
    faceIdx,edgeIdx,vertIdx = mesh_location
    face_edges = myMesh.getFaceEdges(faceIdx)
    assert (edgeIdx in face_edges), "edge {} not in face {}".format(edgeIdx,faceIdx)
    faceTopoVerts = myMesh.getTVertsForFace(faceIdx)
    assert(vertIdx in faceTopoVerts), "prblm in getBasisOnMesh():tVert not in faceTopoVerts "
    edgeTVerts = myMesh.getTVertsForEdge(edgeIdx) 
    assert(vertIdx in edgeTVerts), "prblm in getBasisOnMesh():tVert not part of given edge"
    def getOther(vertIdx, edgeTVerts):
        if(edgeTVerts[0] == vertIdx):
            return edgeTVerts[1]
        elif(edgeTVerts[1] == vertIdx):
            return edgeTVerts[0]
        else:
            print "ERROR: edgeTVerts does not contain vertIdx"
            return None
    pntA = myMesh.get_point_for_tVert(vertIdx)
    pntB = myMesh.get_point_for_tVert(getOther(vertIdx, edgeTVerts))
    x = helper.getVectorForPoints(pntA,pntB)
    normal = geom.Vector3d(myMesh.mesh.FaceNormals.Item[faceIdx])
    return Frame.create_frame_from_normal_and_x(pntA,normal,x)

def get_xy_net_frame(pointPair):
    pntI, pntJ = pointPair
    o = pntI
    x = geom.Vector3d(pntJ - pntI)
    z = geom.Vector3d(0,0,1)
    return Frame.create_frame_from_vectors(o,x,z)

def make_origin_frame():
    plane = rs.WorldXYPlane()
    """
    print "first element of worldXYplane is {}".format(type(plane[0]))
    print "second element of worldXYplane is {}".format(type(plane[1]))
    print "third element of worldXYplane is {}".format(type(plane[2]))
    print "fourth element of worldXYplane is {}".format(type(plane[3]))
    """
    return Frame(plane)

class Frame(object):

    """
    An orthonormal bases: each vector is of unit length
    and all three vectors are orthogonal to one-another
    """
    def __init__(self,plane):
        self.plane = plane #RhinoGeom Plane
        self.precision = .0000001
        self._unitize()
        self._check_unitized()
        self._check_orthogonal()
        self.x_color = {'red':(0,250,32,32)} #a,r,g,b,
        self.y_color = {'green':(0,32,250,32)}
        self.z_color = {'blue':(0,32,32,250)}

    @classmethod
    def create_frame_from_vectors(cls,origin,x,y):
        plane = cls.instantiate_plane(origin,x,y)
        return cls(plane)

    @classmethod
    def create_frame_from_normal_and_x(cls,origin,normal,x):
        '''
        origin = Rhino.Geometry.Point3d
        x,normal = Rhino.Geometry.Vector3d
        '''
        y = geom.Vector3d.CrossProduct(normal,x)
        return cls(cls.instantiate_plane(origin,x,y))

    @classmethod
    def create_frame_from_tuples(cls,origin,x,y):
        origin = geom.Point3d(origin[0],origin[1],origin[2])
        x = geom.Vector3d(x[0],x[1],x[2])
        y = geom.Vector3d(y[0],y[1],y[2])
        plane = cls.instantiate_plane(origin,x,y)
        return cls(plane)

    @staticmethod
    def instantiate_plane(origin,x,y):
        assert x.IsPerpendicularTo(y), "vec {} is not perpendicular to {}".format(x,y)
        return geom.Plane(origin,x,y)

    def show(self):
        visualization.drawVector(self.plane.XAxis,self.plane.Origin,self.x_color['red'])
        visualization.drawVector(self.plane.YAxis,self.plane.Origin,self.y_color['green'])
        visualization.drawVector(self.plane.ZAxis,self.plane.Origin,self.z_color['blue'])

    def is_equal(self,test_frame):
        return self.plane.Equals(test_frame.plane)

    def _check_vector3d(self):
        pass

    def _unitize(self):
        self.plane.XAxis.Unitize()
        self.plane.YAxis.Unitize()
        self.plane.ZAxis.Unitize()

    def _check_orthogonal(self):
        xy = geom.Vector3d.Multiply(self.plane.XAxis,self.plane.YAxis)
        assert(math.fabs(xy)< self.precision)
        yz = geom.Vector3d.Multiply(self.plane.YAxis,self.plane.ZAxis)
        assert(math.fabs(yz)< self.precision)
        zx = geom.Vector3d.Multiply(self.plane.ZAxis,self.plane.XAxis)
        assert(math.fabs(zx)< self.precision)

    def _check_unitized(self):
        assert(self.plane.XAxis.Length - 1 < .00000001), "x.Length!~=1"
        assert(self.plane.YAxis.Length - 1 < .00000001), "y.Length!~=1"
        assert(self.plane.ZAxis.Length - 1 < .00000001), "z.Length!~=1"

if __name__ == "__main__":
    make_origin_frame()
