import Rhino
import rhinoscriptsyntax as rs
import System.Drawing

def displayNormals(mesh):
	normLines = []
	for i in range(mesh.FaceNormals.Count):
		p1 = mesh.Faces.GetFaceCenter(i)
		p2 = p1 + mesh.FaceNormals.Item[i]
		normLines.append(rs.AddLine(p1,p2))
	createGroup("normLines",normLines)

def displayFaceIdxs(mesh):
	for i in xrange(mesh.Faces.Count):
		centerPnt = mesh.Faces.GetFaceCenter(i)
		rs.AddTextDot(str(i),centerPnt)


def displayEdgeIdx(line,edgeIdx):
	cenX = (line.FromX+line.ToX)/2
	cenY = (line.FromY+line.ToY)/2
	cenZ = (line.FromZ+line.ToZ)/2
	eIdx = str(edgeIdx)
	rs.AddTextDot(eIdx,[cenX,cenY,cenZ])

def displayDual(faces,edge_weights,thetaMax,mesh):
	medianEdgeLen = getMedianEdgeLen(mesh)
	aspectRatio = 1/10.0
	scaleFactor = medianEdgeLen*aspectRatio
	dualRods = []
	for tupEdge in edge_weights:
		edgeIdx = tupEdge[0]
		weight = tupEdge[1]
		r = (weight/thetaMax)*scaleFactor
		connFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIdx)
		faceCenter0 = mesh.Faces.GetFaceCenter(connFaces.GetValue(0))
		faceCenter1 = mesh.Faces.GetFaceCenter(connFaces.GetValue(1))

		dualRods.append(rs.AddCylinder(faceCenter0,faceCenter1,r))
	createGroup("dualRods",dualRods)
		
def createGroup(groupName,objects):
	name = rs.AddGroup(groupName)
	if not rs.AddObjectsToGroup(objects,groupName):
		print "failed to group"

def convertArray(array):
	pyList = []
	for i in range(array.Length):
		pyList.append(array.GetValue(i))
	return pyList

def setAttrColor(a,r,g,b):
	attr = Rhino.DocObjects.ObjectAttributes()
	attr.ObjectColor = System.Drawing.Color.FromArgb(a,r,g,b)
	attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
	return attr

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