#test mesh edge direction
from visualization import *
from rhino_helpers import *
from rhino_inputs import getUserCuts, getMesh


mesh = getMesh("select mesh")
edgeIdxs = getUserCuts("select edge")
displayIJEdge(mesh,edgeIdxs[0])
vec = getEdgeVector(mesh,edgeIdxs[0])
endPnt = Rhino.Geometry.Point3d(vec)
origin = Rhino.Geometry.Point3d(0,0,0)
drawLine([origin,endPnt],(0,0,0,0),'EndArrowhead')

'''Verified: vec point from I to J !!
'''