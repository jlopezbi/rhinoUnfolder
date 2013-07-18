# test_getTabAngles

from visualization import *
from rhino_helpers import *
from rhino_inputs import getUserCuts, getMesh
from classes import FlatEdge

mesh = getMesh("select mesh")
edgeIdxs = getUserCuts("select edge")
edgeIdx = edgeIdxs[0]
faceIdxs = getFacesForEdge(mesh, edgeIdx)
faceIdx = faceIdxs[0]

# coordinates = getPointsForEdge(mesh,edgeIdx)

# flatEdge = FlatEdge(edgeIdx,coordinates)

FlatEdge.getTabAngles(mesh,faceIdx,edgeIdx)

