import Rhino
from rhino_helpers import *

def createTransformMatrix(fromBasis,toBasis):
  p = fromBasis[0]
  u = fromBasis[1]
  v = fromBasis[2]
  w = fromBasis[3]

  o = toBasis[0]
  i = toBasis[1]
  j = toBasis[2]
  k = toBasis[3]

  o = Rhino.Geometry.Vector3d(o)
  p = Rhino.Geometry.Vector3d(p)

  changeBasisXform = Rhino.Geometry.Transform.ChangeBasis(u,v,w,i,j,k)

  transFormToOrigin = Rhino.Geometry.Transform.Translation(-p)
  rotatXform = Rhino.Geometry.Transform.Rotation(u,v,w,i,j,k)
  transFormToPnt = Rhino.Geometry.Transform.Translation(o)
  xForm1 = Rhino.Geometry.Transform.Multiply(rotatXform,transFormToOrigin)
  xForm2 = Rhino.Geometry.Transform.Multiply(transFormToPnt,xForm1)

  transXform = Rhino.Geometry.Transform.Translation(o-p)
  fullXform = Rhino.Geometry.Transform.Multiply(rotatXform,transXform)

  return xForm2

def getBasisOnMesh(basisInfo,mesh):
  faceIdx,edgeIdx,tVertIdx = basisInfo
  faceTopoVerts = convertArray(mesh.Faces.GetTopologicalVertices(faceIdx))
  assert(tVertIdx in faceTopoVerts),"prblm in getBasisOnMesh():tVert not in faceTopoVerts "
  edgeTopoVerts = [mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I,mesh.TopologyEdges.GetTopologyVertices(edgeIdx).J]
  assert(tVertIdx in edgeTopoVerts),"prblm in getBasisOnMesh():tVert not part of given edge"
  def getOther(tVertIdx,edgeTopoVerts):
    if(edgeTopoVerts[0]==tVertIdx):
      return edgeTopoVerts[1]
    elif(edgeTopoVerts[1]==tVertIdx):
      return edgeTopoVerts[0]
    else:
      print "ERROR: edgeTopoVerts does not contain tVertIdx"
      return None

  """U"""
  p1 = mesh.TopologyVertices.Item[tVertIdx]
  p2 = mesh.TopologyVertices.Item[getOther(tVertIdx,edgeTopoVerts)]

  pU = p2-p1
  u = Rhino.Geometry.Vector3d(pU)
  u.Unitize()

  """W"""
  w = Rhino.Geometry.Vector3d(mesh.FaceNormals.Item[faceIdx])
  w.Unitize()

  """V"""
  v = Rhino.Geometry.Vector3d.CrossProduct(w,u)
  v.Unitize()

  """P"""
  p = mesh.TopologyVertices.Item[tVertIdx]

  return [p,u,v,w]

def getTransform(basisInfo,toBasis,mesh):
  fromBasis = getBasisOnMesh(basisInfo,mesh)
  xForm = createTransformMatrix(fromBasis,toBasis)
  return xForm

def getBasisFlat(newCoords):
  #Convention: always use .I element from the tVerts associated with a given edge
  o = newCoords[0]
  #assert(o.Z==0), "newCoord has Z compenent!"
  #print "o.z:%1.2f"%o.Z
  x = Rhino.Geometry.Vector3d(newCoords[1]-newCoords[0])
  x.Unitize()
  z = rs.WorldXYPlane()[3]
  #z = Rhino.Geometry.Vector3d(0.0,0.0,1.0)
  z.Unitize()
  y = Rhino.Geometry.Vector3d.CrossProduct(z,x)
  y.Unitize()

  assert(x.Length-1<.00000001), "x.Length!~=1"
  assert(y.Length-1<.00000001), "y.Length!~=1"
  assert(z.Length-1<.00000001), "z.Length!~=1"

  return [o,x,y,z]
