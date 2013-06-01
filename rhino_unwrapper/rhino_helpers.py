import Rhino
import rhinoscriptsyntax as rs

def connectedFaces(mesh, edgeIndex):
  arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIndex)

  faceIdx0 = arrConnFaces.GetValue(0)
  faceIdx1 = arrConnFaces.GetValue(1)

  return faceIdx0, faceIdx1

def getMesh(message=None):
  getter = Rhino.Input.Custom.GetObject()
  getter.SetCommandPrompt(message)
  getter.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh
  getter.SubObjectSelect = True
  getter.Get()
  if getter.CommandResult() != Rhino.Commands.Result.Success:
    return

  objref = getter.Object(0)
  obj = objref.Object()
  mesh = objref.Mesh()

  obj.Select(False)

  if obj:
    return mesh

def createGroup(groupName,objects):
	name = rs.AddGroup(groupName)
	if not rs.AddObjectsToGroup(objects,groupName):
		print "failed to group"

def convertArray(array):
	pyList = []
	for i in range(array.Length):
		pyList.append(array.GetValue(i))
	return pyList

def getFaceEdges(faceIdx,mesh):
	arrFaceEdges = mesh.TopologyEdges.GetEdgesForFace(faceIdx)
	return convertArray(arrFaceEdges)

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

def getEdgeLen(edgIdx,mesh):
	edgeLine = mesh.TopologyEdges.EdgeLine(edgeIdx)
	return edgeLine.Length

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