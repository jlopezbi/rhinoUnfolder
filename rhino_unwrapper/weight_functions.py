import Rhino
import rhinoscriptsyntax as rs
import rhino_helpers as rh

def edgeAngle(mesh, edgeIndex):
  faceIdxs = rh.getFacesForEdge(mesh, edgeIndex)

  if (len(faceIdxs)==2):
    faceNorm0 = mesh.FaceNormals.Item[faceIdxs[0]]
    faceNorm1 = mesh.FaceNormals.Item[faceIdxs[1]]
    return rs.VectorAngle(faceNorm0,faceNorm1) 
  else:
    return None

def uniform(mesh, edgeIndex):
  return 1

import random as rand

def random(mesh, edgeIndex):
  return rand.random()

def planeAligned(mesh,edgeIdx):
  planeNormal = Rhino.Geometry.Vector3d(1,0,0)
  edgeVec = rh.getEdgeVector(mesh,edgeIdx)
  angle = rh.angleBetweenVecAndPlane(edgeVec,planeNormal)
  return 1.0/(angle+.000000001)