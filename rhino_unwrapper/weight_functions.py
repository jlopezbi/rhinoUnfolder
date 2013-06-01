import rhinoscriptsyntax as rs

from rhino_helpers import connectedFaces

def edgeAngle(mesh, edgeIndex):
  faceIdx0, faceIdx1 = connectedFaces(mesh, edgeIndex)

  faceNorm0 = mesh.FaceNormals.Item[faceIdx0]
  faceNorm1 = mesh.FaceNormals.Item[faceIdx1]

  return rs.VectorAngle(faceNorm0,faceNorm1) # returns None on error