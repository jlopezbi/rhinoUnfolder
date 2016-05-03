import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System.Drawing

import math,collections

# TODO: look into inline functions

'''Rhino_helpers'''

def createGroup(groupName, objects):
    name = rs.AddGroup(groupName)
    if not rs.AddObjectsToGroup(objects, groupName):
        print "failed to group"
        return
    return name

def convertArray(array):
    return list(array)

def rotate_and_remove(sequence,index):
    #TODO: Test function
    '''
    returns deque list rotated so starts with element after index
    Examples:
    rotate_and_remove[(4,3,1,6],2) => [6,4,3] 
    rotate_and_remove[(4,3,1,6],1) => [1,6,4] 
    '''
    value = sequence[index]
    sequence = collections.deque(sequence)
    sequence.rotate(-index)
    sequence.remove(value)
    return list(sequence)

def getCenterPointLine(line):
    cenX = (line.FromX + line.ToX) / 2
    cenY = (line.FromY + line.ToY) / 2
    cenZ = (line.FromZ + line.ToZ) / 2
    point = Rhino.Geometry.Point3d(cenX, cenY, cenZ)
    return point

def getOffset(points, testPoint, distance, towards, axis=(0, 0, 1)):
    '''
    points = list of two Point3d points making up the line to be offset
    testPoint = point which determines which side to offset
    distance = distance to offset
    towards = boolean, determine if offset should be towards testPoint or away
    axis = axis about which to rotate
    ouput:
      returns a Rhino.Geometry.Line() object
    '''
    axisVec = Rhino.Geometry.Vector3d(axis[0], axis[1], axis[2])
    vec = Rhino.Geometry.Vector3d(points[1] - points[0])
    vecChange = Rhino.Geometry.Vector3d(vec)
    vecChange.Unitize()
    onLeft = testPointIsLeftB(points[0], points[1], testPoint)
    angle = math.pi / 2.0  # default is (+) to the left
    if not onLeft:
        angle = -1.0 * angle
    if not towards:
        angle = -1.0 * angle
    vecChange.Rotate(angle, axisVec)
    offsetVec = Rhino.Geometry.Vector3d.Multiply(vecChange, distance)
    offsetPoint = Rhino.Geometry.Point3d(offsetVec)
    point = offsetPoint + points[0]
    return Rhino.Geometry.Line(point, vec), offsetVec

def testPointIsLeftB(pointA, pointB, testPoint):
    '''
    ASSUMES: in XY plane!!!
    use cross product to see if testPoint is to the left of
    the directed line formed from pointA to pointB
    returns False if co-linear.
    '''
    vecLine = getVectorForPoints(pointA, pointB)
    vecTest = getVectorForPoints(pointA, testPoint)
    cross = Rhino.Geometry.Vector3d.CrossProduct(vecLine, vecTest)
    z = cross.Z  # (pos and neg)
    return z > 0

def getVectorForPoints(pntA, pntB):
    vecA = Rhino.Geometry.Vector3d(pntA)  # From
    vecB = Rhino.Geometry.Vector3d(pntB)  # To
    return Rhino.Geometry.Vector3d.Subtract(vecB, vecA)

def getMidPoint(curve_id):
    '''get the midpoint of a curve
    '''
    startPnt = rs.CurveStartPoint(curve_id)
    endPnt = rs.CurveEndPoint(curve_id)

    cenX = (startPnt.X + endPnt.X) / 2
    cenY = (startPnt.Y + endPnt.Y) / 2
    cenZ = (startPnt.Z + endPnt.Z) / 2
    point = Rhino.Geometry.Point3d(cenX, cenY, cenZ)

    return point

def getMedian(edgeLens):
    eLensSorted = sorted(edgeLens)
    nEdges = len(edgeLens)
    assert(nEdges > 0), "nEdges is !>0, error in getMedianEdgeLen()"
    if nEdges % 2 == 0:
        idxUpper = nEdges / 2
        idxLower = idxUpper - 1
        avg = (edgeLens[idxUpper] + edgeLens[idxLower]) / 2.0
        return avg
    else:
        return edgeLens[int(nEdges / 2)]

def approxEqual(A, B, tolerance=10**-4):
    return math.fabs(A - B) < tolerance

def getFlatList(collection):
    return [element for subCollection in collection for element in subCollection]

def uniqueList(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result
