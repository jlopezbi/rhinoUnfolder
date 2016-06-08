import rhinoscriptsyntax as rs
import random as rand

def edgeAngle(myMesh, edgeIndex):
    #TODO: make myMesh function which findes angel between two faces of a given edge
    faceIdxs = myMesh.getFacesForEdge(edgeIndex)
    if (len(faceIdxs) == 2):
        faceNorm0 = myMesh.face_normal(faceIdxs[0])
        faceNorm1 = myMesh.face_normal(faceIdxs[1])
        return rs.VectorAngle(faceNorm0, faceNorm1)
    else:
        return None

def uniform(mesh, edgeIndex):
    return 1

def random(mesh, edgeIndex):
    return rand.random()
