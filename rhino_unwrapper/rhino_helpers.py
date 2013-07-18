import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System.Drawing



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

def getFacesForEdge(mesh, edgeIndex):
  '''
  returns an array of indices of the faces connected to a given edge
  if the array has only one face this inidicates it is a naked edge
  should be changed to get any number of faces, and return None if couldnt find 
  any faces
  '''
  arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIndex)

  faceIdxs = []
  faceIdxs.append(arrConnFaces.GetValue(0))
  if arrConnFaces.Length == 2:
    faceIdxs.append(arrConnFaces.GetValue(1))

  return faceIdxs

def getOtherFaceIdx(edgeIdx,faceIdx,mesh):
  connectedFaces = getFacesForEdge(mesh,edgeIdx)
  #assert(len(connectedFaces)==2),"getOtherFaceIdx(): did not get two connected Faces"
  assert(faceIdx in connectedFaces),"getOtherFaceIdx(): faceIdx not in faces associated with edge"

  nakedEdges = mesh.GetNakedEdges()
  if nakedEdges !=None and edgeIdx in mesh.GetNakedEdges():
      return 

  if len(connectedFaces) != 2:
    #This is a naked edge
    #print("did not find two connected faces for edgeIdx %i, " %(edgeIdx))
    return
    
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

def getFaceEdges(faceIdx,mesh):
  arrFaceEdges = mesh.TopologyEdges.GetEdgesForFace(faceIdx)
  return convertArray(arrFaceEdges)

def getTVerts(edgeIdx,mesh):
  vertPair = mesh.TopologyEdges.GetTopologyVertices(edgeIdx)
  return vertPair.I, vertPair.J

def getPointsForEdge(mesh,edgeIdx):
  tVertI,tVertJ = getTVerts(edgeIdx,mesh)
  pntI = mesh.TopologyVertices.Item[tVertI]
  pntJ = mesh.TopologyVertices.Item[tVertJ]
  return [pntI,pntJ]

def getMedianEdgeLen(mesh):
  edgeLens = getEdgeLengths(mesh)
  return getMedian(edgeLens)

def getEdgeLengths(mesh):
  edgeLens = []
  for i in range(mesh.TopologyEdges.Count):
    edgeLine = mesh.TopologyEdges.EdgeLine(i)
    edgeLen = edgeLine.Length
    edgeLens.append(edgeLen)
  return edgeLens

def getEdgeVector(mesh,edgeIdx):
  edgeLine = mesh.TopologyEdges.EdgeLine(edgeIdx)
  #Vector3d
  vec = edgeLine.Direction
  return vec

# def getVectorForPoints(pntA,pntB):
#   vecA = Rhino.Geometry.Vector3d(pntA)
#   vecB = Rhino.Geometry

def getEdgeLen(edgIdx,mesh):
  edgeLine = mesh.TopologyEdges.EdgeLine(edgeIdx)
  return edgeLine.Length

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