import rhinoscriptsyntax as rs

import rhino_helpers


def edgeAngle(myMesh, edgeIndex):
    faceIdxs = myMesh.getFacesForEdge(edgeIndex)

    if (len(faceIdxs) == 2):
        faceNorm0 = myMesh.mesh.FaceNormals.Item[faceIdxs[0]]
        faceNorm1 = myMesh.mesh.FaceNormals.Item[faceIdxs[1]]
        return rs.VectorAngle(faceNorm0, faceNorm1)
    else:
        return None


def uniform(mesh, edgeIndex):
    return 1

import random as rand


def random(mesh, edgeIndex):
    return rand.random()
