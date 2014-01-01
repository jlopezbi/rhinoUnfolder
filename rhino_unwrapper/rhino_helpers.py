import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System.Drawing
import math

#TODO: look into inline functions

'''Rhino_helpers'''
def createGroup(groupName,objects):
  name = rs.AddGroup(groupName)
  if not rs.AddObjectsToGroup(objects,groupName):
    print "failed to group"
    return
  return name

def convertArray(array):
  pyList = []
  for i in range(array.Length):
    pyList.append(array.GetValue(i))
  return pyList

def getOtherFaceIdx(edgeIdx,faceIdx,mesh):
  connectedFaces = getFacesForEdge(mesh,edgeIdx)
  assert(faceIdx in connectedFaces),"faceIdx not in faces associated with edge"

  if len(connectedFaces) != 2:
    #This is a naked edge
    #print("did not find two connected faces for edgeIdx %i, " %(edgeIdx))
    return -1
    
  newFaceIdx = None
  if (connectedFaces[0]==faceIdx):
    newFaceIdx = connectedFaces[1]
  elif (connectedFaces[1]==faceIdx):
    newFaceIdx = connectedFaces[0]
  else:
    print "problem in getOtherFaceIdx: edgeIdx not in faceIdx,assert should have caught error"
    return None

  assert(newFaceIdx!=faceIdx), "getOtherFaceIdx(): newFaceIdx == faceIdx!"
  return newFaceIdx

def getCenterPointLine(line):
  cenX = (line.FromX+line.ToX)/2
  cenY = (line.FromY+line.ToY)/2
  cenZ = (line.FromZ+line.ToZ)/2
  point = Rhino.Geometry.Point3d(cenX,cenY,cenZ)
  return point

'''VERT INFO'''

def getTVertsForVert(mesh,tVert):
  arrTVerts = mesh.TopologyVertices.ConnectedTopologyVertices(tVert)
  listVerts = convertArray(arrTVerts)
  if tVert in listVerts:
    listVerts = listVerts.remove(tVert)
  return listVerts

def getEdgesForVert(mesh,tVert):
  #not implimented in rhinoCommon! ::::(
  #rather inefficient
  neighVerts = getTVertsForVert(mesh,tVert)
  facesVert = set(getFacesforVert(mesh,tVert))
  edges = []
  for neighVert in neighVerts:

    edge = getEdgeForTVertPair(mesh,tVert,neighVert,facesVert)
    if edge:
      edges.append(edge)
  return edges

def getEdgeForTVertPair(mesh,tVertA,tVertB,facesVertA=None):
  if facesVertA == None:
    facesVertA = getFacesforVert(mesh,tVertA)
  facesVertB = set(getFacesforVert(mesh,tVertB))
  facePair = list(facesVertA.intersection(facesVertB))
  if len(facePair)==2:
    edgesA = set(getFaceEdges(facePair[0],mesh))
    edgesB = set(getFaceEdges(facePair[1],mesh))
    edge = edgesA.intersection(edgesB)
    if len(edge)==0:
      print "probably encountered naked edge in chain selection"
      return
    return list(edge)[0]
  elif len(facePair)==1:
    #naked edge
    edges = getFaceEdges(facePair[0],mesh)
    for edge in edges:
      tVerts = getTVertsForEdge(mesh,edge)
      if tVertB in tVerts and tVertA in tVerts:
        return edge
  return


def getFacesforVert(mesh,tVert):
  arrfaces = mesh.TopologyVertices.ConnectedFaces(tVert)
  return convertArray(arrfaces)

''' EDGE INFO'''
def getTVertsForEdge(mesh,edge):
  vertPair = mesh.TopologyEdges.GetTopologyVertices(edge)
  return [vertPair.I, vertPair.J]

def getFacesForEdge(mesh, edgeIndex):
  '''
  returns an array of indices of the faces connected to a given edge
  if the array has only one face this indicates it is a naked edge
  '''
  arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIndex)

  faceIdxs = []
  faceIdxs.append(arrConnFaces.GetValue(0))
  if arrConnFaces.Length == 2:
    faceIdxs.append(arrConnFaces.GetValue(1))

  return faceIdxs
  
def getChain(mesh,edge,angleTolerance):
  '''
  gets chains extending from both ends of a given edge,
  using angleTolerance as stopping criterion
  '''
  chain = []
  tVerts = getTVertsForEdge(mesh,edge)
  for tVert in tVerts:
    subChain = getTangentEdge(mesh,edge,tVert,angleTolerance,[])
    chain.extend(subChain)
  chain.append(edge)
  return chain

def getTangentEdge(mesh,edge,tVert,angleTolerance,chain):
  '''
  return edge that is closest in angle, or none if none
  of the edges are within angleTolerance
  '''
  edges = getEdgesForVert(mesh,tVert)
  if edge in edges: edges.remove(edge)
  winEdge = (None,angleTolerance)
  for neighEdge in edges:
    angle  = compareEdgeAngle(mesh,edge,tVert,neighEdge)
    if angle<angleTolerance and angle<winEdge[1]:
      winEdge = (neighEdge,angle)

  newEdge = winEdge[0]
  if newEdge == None:
    return chain
  if newEdge in chain:
    return chain
  else:
    chain.append(newEdge)
    nextTVert = getOtherTVert(mesh,newEdge,tVert)
    return getTangentEdge(mesh,newEdge,nextTVert,angleTolerance,chain)

def getDistanceToEdge(mesh,edge,point):
  '''
  edge = Topology edgeIdx in mesh
  point = Point3d to get distance to edge
  '''
  edgeLine = mesh.TopologyEdges.EdgeLine(edge)
  return edgeLine.DistanceTo(point,True)

def getEdgeVector(mesh,edgeIdx):
  edgeLine = mesh.TopologyEdges.EdgeLine(edgeIdx)
  #Vector3d
  vec = edgeLine.Direction
  return vec

def getOtherTVert(mesh,edge,tVert):
  tVerts = getTVertsForEdge(mesh,edge)
  tVerts.remove(tVert)
  return tVerts[0]

def getPointsForEdge(mesh,edgeIdx):
  tVertI,tVertJ = getTVertsForEdge(mesh,edgeIdx)
  pntI = mesh.TopologyVertices.Item[tVertI]
  pntJ = mesh.TopologyVertices.Item[tVertJ]
  return [pntI,pntJ]

def getEdgeLen(edgIdx,mesh):
  edgeLine = mesh.TopologyEdges.EdgeLine(edgeIdx)
  return edgeLine.Length

def compareEdgeAngle(mesh,edge,tVert,neighEdge):
  vecBase = getOrientedVector(mesh,edge,tVert,True)
  vecCompare = getOrientedVector(mesh,neighEdge,tVert,False)
  angle = Rhino.Geometry.Vector3d.VectorAngle(vecBase,vecCompare)
  return angle

def getEdgeLengths(mesh):
  edgeLens = []
  for i in range(mesh.TopologyEdges.Count):
    edgeLine = mesh.TopologyEdges.EdgeLine(i)
    edgeLen = edgeLine.Length
    edgeLens.append(edgeLen)
  return edgeLens


'''FACE INFO'''
def getTVertsForFace(mesh,faceIdx):
  '''
  list of 4 values if quad, 3 values if triangle
  '''
  arrTVerts = mesh.Faces.GetTopologicalVertices(faceIdx)
  tVerts = convertArray(arrTVerts)
  return uniqueList(tVerts)

def getFaceEdges(faceIdx,mesh):
  arrFaceEdges = mesh.TopologyEdges.GetEdgesForFace(faceIdx)
  return convertArray(arrFaceEdges)

'''MESH INFO'''

def getMedianEdgeLen(mesh):
  edgeLens = getEdgeLengths(mesh)
  return getMedian(edgeLens)

'''UNCATEGORIZED'''

def angleBetweenVecAndPlane(vec,planeNormal):
  return math.asin(math.fabs(vec*planeNormal)/(vec.Length*planeNormal.Length))

def getOffset(points,testPoint,distance,towards,axis=(0,0,1)):
  '''
  points = list of two Point3d points making up the line to be offset
  testPoint = point which determines which side to offset
  distance = distance to offset
  towards = boolean, determine if offset should be towards testPoint or away
  axis = axis about which to rotate
  ouput:
    returns a Rhino.Geometry.Line() object
  '''
  axisVec = Rhino.Geometry.Vector3d(axis[0],axis[1],axis[2])
  vec = Rhino.Geometry.Vector3d(points[1]-points[0])
  vecChange = Rhino.Geometry.Vector3d(vec)
  vecChange.Unitize()
  onLeft = testPointIsLeftB(points[0],points[1],testPoint)
  angle = math.pi/2.0 # default is (+) to the left
  if not onLeft:
    angle = -1.0*angle
  if not towards:
    angle = -1.0*angle
  vecChange.Rotate(angle,axisVec)
  offsetVec = Rhino.Geometry.Vector3d.Multiply(vecChange,distance)
  offsetPoint = Rhino.Geometry.Point3d(offsetVec)
  point = offsetPoint+points[0]
  return Rhino.Geometry.Line(point,vec),offsetVec

def testPointIsLeftB(pointA,pointB,testPoint):
  '''
  ASSUMES: in XY plane!!!
  use cross product to see if testPoint is to the left of 
  the directed line formed from pointA to pointB
  returns False if co-linear.
  '''
  vecLine = getVectorForPoints(pointA,pointB)
  vecTest = getVectorForPoints(pointA,testPoint)
  cross = Rhino.Geometry.Vector3d.CrossProduct(vecLine,vecTest)
  z = cross.Z #(pos and neg)
  return  z > 0 

def getOrientedVector(mesh,edgeIdx,tVert,isEnd):
  '''
  tVert is the end point of this vector
  '''
  tVerts = getTVertsForEdge(mesh,edgeIdx)
  assert(tVert in tVerts)
  tVerts.remove(tVert)
  otherVert = tVerts[0]
  if isEnd:
    pntB = mesh.TopologyVertices.Item[tVert]
    pntA = mesh.TopologyVertices.Item[otherVert]
  else:
    pntA = mesh.TopologyVertices.Item[tVert]
    pntB = mesh.TopologyVertices.Item[otherVert]  
  vecPnt = pntB-pntA
  vec = Rhino.Geometry.Vector3d(vecPnt)
  return vec

def getVectorForPoints(pntA,pntB):
  vecA = Rhino.Geometry.Vector3d(pntA) #From
  vecB = Rhino.Geometry.Vector3d(pntB) #To
  return  Rhino.Geometry.Vector3d.Subtract(vecB,vecA)

def getMidPoint(curve_id):
  '''get the midpoint of a curve
  '''
  startPnt = rs.CurveStartPoint(curve_id)
  endPnt = rs.CurveEndPoint(curve_id)

  cenX = (startPnt.X+endPnt.X)/2
  cenY = (startPnt.Y+endPnt.Y)/2
  cenZ = (startPnt.Z+endPnt.Z)/2
  point = Rhino.Geometry.Point3d(cenX,cenY,cenZ)

  return point

def getMedian(edgeLens):
  eLensSorted = sorted(edgeLens)
  nEdges = len(edgeLens)
  assert(nEdges>0), "nEdges is !>0, error in getMedianEdgeLen()"
  if nEdges%2 ==0:
    idxUpper = nEdges/2
    idxLower = idxUpper-1
    avg = (edgeLens[idxUpper]+edgeLens[idxLower])/2.0
    return avg
  else:
    return edgeLens[int(nEdges/2)]

def approxEqual(A,B,tolerance=10**-4):
  return math.fabs(A-B)<tolerance

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
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

