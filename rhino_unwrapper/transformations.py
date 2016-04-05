from rhino_helpers import *
import visualization 
import math

reload(visualization)



def createTransformMatrix(from_frame, to_frame):
    p, u, v, w = from_frame.get_tuple()
    o, i, j, k = to_frame.get_tuple()

    o = Rhino.Geometry.Vector3d(o)
    p = Rhino.Geometry.Vector3d(p)

    changeBasisXform = Rhino.Geometry.Transform.ChangeBasis(u, v, w, i, j, k)

    transFormToOrigin = Rhino.Geometry.Transform.Translation(-p)
    rotatXform = Rhino.Geometry.Transform.Rotation(u, v, w, i, j, k)
    transFormToPnt = Rhino.Geometry.Transform.Translation(o)
    xForm1 = Rhino.Geometry.Transform.Multiply(rotatXform, transFormToOrigin)
    xForm2 = Rhino.Geometry.Transform.Multiply(transFormToPnt, xForm1)

    transXform = Rhino.Geometry.Transform.Translation(o - p)
    fullXform = Rhino.Geometry.Transform.Multiply(rotatXform, transXform)

    return xForm2

def getBasisOnMesh(mesh_frame, mesh):
    faceIdx, edgeIdx, tVertIdx = mesh_frame
    faceTopoVerts = convertArray(mesh.Faces.GetTopologicalVertices(faceIdx))
    assert(tVertIdx in faceTopoVerts), "prblm in getBasisOnMesh():tVert not in faceTopoVerts "
    edgeTopoVerts = [mesh.TopologyEdges.GetTopologyVertices(
        edgeIdx).I, mesh.TopologyEdges.GetTopologyVertices(edgeIdx).J]
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
    p1 = mesh.TopologyVertices.Item[tVertIdx]
    p2 = mesh.TopologyVertices.Item[getOther(tVertIdx, edgeTopoVerts)]
    pU = p2 - p1
    u = Rhino.Geometry.Vector3d(pU)
    """W"""
    w = Rhino.Geometry.Vector3d(mesh.FaceNormals.Item[faceIdx])
    """P"""
    origin = mesh.TopologyVertices.Item[tVertIdx]
    return Frame.create_frame(origin,u,w)


def getTransform(meshFrame, toBasis, mesh):
    fromBasis = getBasisOnMesh(meshFrame, mesh)
    xForm = createTransformMatrix(fromBasis, toBasis)
    return xForm

def get_net_frame(pointPair):
    pntI, pntJ = pointPair
    o = pntI
    x = Rhino.Geometry.Vector3d(pntJ - pntI)
    z = rs.WorldXYPlane()[3]
    return Frame.create_frame(o,x,z)

#Frame = collections.namedtuple('Frame',['origin','xVec','yVec','zVec'])

class Frame(object):

    """
    An orthonormal bases: each vector is of unit length
    and all three vectors are orthogonal to one-another
    """
    def __init__(self,origin,xVec,yVec,zVec):
        self.origin = origin
        self.xVec = xVec
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

    def test_self(self):
        print type(self.origin)

if __name__ == "__main__":
    pass
