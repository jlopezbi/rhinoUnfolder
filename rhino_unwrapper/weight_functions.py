import rhinoscriptsyntax as rs

import rhino_helpers

def edgeAngle(mesh, edgeIndex):
  faceIdxs = rhino_helpers.connectedFaces(mesh, edgeIndex)

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
