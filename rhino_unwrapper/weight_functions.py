import rhinoscriptsyntax as rs

import rhino_helpers

def edgeAngle(mesh, edgeIndex):
  faceIdx0, faceIdx1 = rhino_helpers.connectedFaces(mesh, edgeIndex)

  faceNorm0 = mesh.FaceNormals.Item[faceIdx0]
  faceNorm1 = mesh.FaceNormals.Item[faceIdx1]

  return rs.VectorAngle(faceNorm0,faceNorm1) # returns None on error

def uniform(mesh, edgeIndex):
  return 1

import random as rand
def random(mesh, edgeIndex):
  return rand.random()
