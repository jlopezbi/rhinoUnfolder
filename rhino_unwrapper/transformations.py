from rhino_helpers import *
import visualization 
import math

reload(visualization)


def createTransformMatrix(from_frame, to_frame):
    p, u, v, w = from_frame.get_tuple()
    o, i, j, k = to_frame.get_tuple()

    changeBasisXform = Rhino.Geometry.Transform.ChangeBasis(u, v, w, i, j, k)

    transFormToOrigin = Rhino.Geometry.Transform.Translation(-p)
    rotatXform = Rhino.Geometry.Transform.Rotation(u, v, w, i, j, k)
    transFormToPnt = Rhino.Geometry.Transform.Translation(o)
    xForm1 = Rhino.Geometry.Transform.Multiply(rotatXform, transFormToOrigin)
    xForm2 = Rhino.Geometry.Transform.Multiply(transFormToPnt, xForm1)

    transXform = Rhino.Geometry.Transform.Translation(o - p)
    fullXform = Rhino.Geometry.Transform.Multiply(rotatXform, transXform)

    return xForm2

def get_frame_on_mesh(mesh_location, myMesh):
    faceIdx, edgeIdx = mesh_location
    face_edges = myMesh.getFaceEdges(faceIdx)
    assert(edgeIdx in face_edges), "prblm in get_frame_on_mesh(): edgeIdx not in face_edges"
    #assert(tVertIdx in faceTopoVerts), "prblm in getBasisOnMesh():tVert not in faceTopoVerts "
    """
    edgeTopoVerts = myMesh.getTVertsForEdge(edgeIdx) 
    assert(tVertIdx in edgeTopoVerts), "prblm in getBasisOnMesh():tVert not part of given edge"

    def getOther(tVertIdx, edgeTopoVerts):
        if(edgeTopoVerts[0] == tVertIdx):
            return edgeTopoVerts[1]
        elif(edgeTopoVerts[1] == tVertIdx):
            return edgeTopoVerts[0]
        else:
            print "ERROR: edgeTopoVerts does not contain tVertIdx"
            return None

    """U"""
#    p1 = myMesh.mesh.TopologyVertices.Item[tVertIdx]
#    p2 = myMesh.mesh.TopologyVertices.Item[getOther(tVertIdx, edgeTopoVerts)]
#    pU = p2 - p1
#    u = Rhino.Geometry.Vector3d(pU)
"""
    u = myMesh.getEdgeVector(edgeIdx)
    
    """W"""
    w = Rhino.Geometry.Vector3d(myMesh.mesh.FaceNormals.Item[faceIdx])
    """P"""
    pntI,pntJ = myMesh.getPointsForEdge(edgeIdx)
    origin_vec = Rhino.Geometry.Vector3d(pntI)
    return Frame.create_frame(origin_vec,u,w)

def get_net_frame(pointPair):
    pntI, pntJ = pointPair
    o = pntI
    x = Rhino.Geometry.Vector3d(pntJ - pntI)
    z = rs.WorldXYPlane()[3]
    return Frame.create_frame(o,x,z)

def make_origin_frame():
    plane = rs.WorldXYPlane()
    """
    print "first element of worldXYplane is {}".format(type(plane[0]))
    print "second element of worldXYplane is {}".format(type(plane[1]))
    print "third element of worldXYplane is {}".format(type(plane[2]))
    print "fourth element of worldXYplane is {}".format(type(plane[3]))
    """
    return Frame(plane[0],plane[1],plane[2],plane[3])


#Frame = collections.namedtuple('Frame',['origin','xVec','yVec','zVec'])

class Frame(object):

    """
    An orthonormal bases: each vector is of unit length
    and all three vectors are orthogonal to one-another
    """
    def __init__(self,origin,xVec,yVec,zVec):
        self.origin = origin
        self.xVec = xVec #Vector3d
        self.yVec = yVec
        self.zVec = zVec
        self.precision = .0000001
        self._unitize()
        self._check_unitized()
        self._check_orthogonal()
        self.x_color = {'red':(0,250,32,32)} #a,r,g,b,
        self.y_color = {'green':(0,32,250,32)}
        self.z_color = {'blue':(0,32,32,250)}

    def get_tuple(self):
        return (self.origin, self.xVec, self.yVec, self.zVec)

    @classmethod
    def create_frame(cls,origin,x,z):
        y = Rhino.Geometry.Vector3d.CrossProduct(z, x)
        return cls(origin,x,y,z)

    def show(self):
        visualization.drawVector(self.xVec,self.origin,self.x_color['red'])
        visualization.drawVector(self.yVec,self.origin,self.y_color['green'])
        visualization.drawVector(self.zVec,self.origin,self.z_color['blue'])

    def make_frame(self,origin,x,z):
        y = Rhino.Geometry.Vector3d.CrossProduct(z, x)
        return Frame(origin,x,y,z)

    def _check_vector3d(self):
        pass

    def _unitize(self):
        self.xVec.Unitize()
        self.yVec.Unitize()
        self.zVec.Unitize()

    def _check_orthogonal(self):
        xy = Rhino.Geometry.Vector3d.Multiply(self.xVec,self.yVec)
        assert(math.fabs(xy)< self.precision)
        yz = Rhino.Geometry.Vector3d.Multiply(self.yVec,self.xVec)
        assert(math.fabs(yz)< self.precision)
        zx = Rhino.Geometry.Vector3d.Multiply(self.zVec,self.xVec)
        assert(math.fabs(zx)< self.precision)

    def _check_unitized(self):
        assert(self.xVec.Length - 1 < .00000001), "x.Length!~=1"
        assert(self.yVec.Length - 1 < .00000001), "y.Length!~=1"
        assert(self.zVec.Length - 1 < .00000001), "z.Length!~=1"

if __name__ == "__main__":
    make_origin_frame()
