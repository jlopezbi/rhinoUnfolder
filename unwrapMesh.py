import rhinoscriptsyntax as rs
import random, math, time
import Rhino
import scriptcontext
import sys
import itertools
import System.Guid


def unwrapper():
	nodeCsvFile = open('trussNodes.csv','rb')
	nodeLines = nodeCsvFile.readlines()
	nodeCsvFile.close()

	rawNodes = []

	for line in nodeLines:
		tokens = line.split(',')
		pnt = [float(item) for item in tokens]
		#rs.AddPoint( pnt)
		rawNodes.append(pnt)

	# print('rawNodes:\n')
	# print rawNodes

	edgeCsvFile = open('trussEdges.csv','rb')
	edgeLines = edgeCsvFile.readlines()
	edgeCsvFile.close()

	rawEdges = []

	for line in edgeLines:
		tokens = line.split(',')
		edge = [int(item) for item in tokens]
		idx1 = edge[0]-1 #matlab is 1-indexed!
		idx2 = edge[1]-1
		#p1 = rawNodes[idx1] 
		#p2 = rawNodes[idx2]
		#rs.AddLine(p1,p2)
		rawEdges.append([idx1,idx2])

	nodes = createGraph(rawNodes,rawEdges)
	print"lenNodes: %d" %len(nodes)
	print"lenRawNodes: %d" %len(rawNodes)
	polylineCoords,faces = getTriangleCoords(nodes)

	mesh_id,mesh = generateMesh(rawNodes,faces)
	faces,connFaces,thetaMax = getDual(mesh)
	displayDual(faces,connFaces,thetaMax,mesh)
	
	displayNormals(mesh)

	


	print('Version:')
	print(sys.version )

def displayNormals(mesh):
	normLines = []
	for i in range(mesh.FaceNormals.Count):
		p1 = mesh.Faces.GetFaceCenter(i)
		p2 = p1 + mesh.FaceNormals.Item[i]
		normLines.append(rs.AddLine(p1,p2))
	createGroup("normLines",normLines)

def displayDual(faces,connFaces,thetaMax,mesh):
	#dualLines = []
	dualRods = []
	medianEdgeLen = getMedianEdgeLen(mesh)
	aspectRatio = 1/10
	scaleFactor = medianEdgeLen*aspectRatio
	for connFacePair in connFaces:
		faceIdx0 = connFacePair[0]
		faceIdx1 = connFacePair[1]
		weight = connFacePair[2]
		r = (weight/thetaMax)*scaleFactor

		faceCenter0 = mesh.Faces.GetFaceCenter(faceIdx0)
		faceCenter1 = mesh.Faces.GetFaceCenter(faceIdx1)
		
		#dualLines.append(rs.AddLine(faceCenter0,faceCenter1))
		dualRods.append(rs.AddCylinder(faceCenter0,faceCenter1,r))
	#createGroup("dualLines",dualLines)
	createGroup("dualRods",dualRods)

def createGroup(groupName,objects):
	name = rs.AddGroup(groupName)
	if not rs.AddObjectsToGroup(objects,groupName):
		print "failed to group"

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

def getSpanningPrimAlgo(faces,connFaces):
	nFaces = len(faces)
	spanningTree = []
	count = 0
	while count<nFaces:
		if count ==0:
			faceIdx = random.randint(0,nFaces-1)



def getDual(mesh):
	#input: 
	#	mesh
	#ouput:
	#	faces = list of Faces as MeshFace class (4.rhino3d.com/5/rhinocommon/)
	#	connFaces = list of tuples (faceIdx1,faceIdx2,weight)
	faces = []
	thetaMax = -1
	for i in range(mesh.Faces.Count):
		faces.append(mesh.Faces.GetFace(i))
	connFaces = []
	for i in range(mesh.TopologyEdges.Count):
		arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(i)

		f0 = arrConnFaces.GetValue(0)
		f1 = arrConnFaces.GetValue(1)
		angWeight = calculateAngle(arrConnFaces,mesh)
		if angWeight > thetaMax:
			thetaMax = angWeight
		tupleConnFaces = (f0,f1,angWeight)
		connFaces.append(tupleConnFaces)
	connFaces = sorted(connFaces,key=lambda tup: tup[2])
	
	#pretty2DListPrint(connFaces)

	return faces,connFaces,thetaMax

def pretty2DListPrint(array):
	print "\n".join(" ".join(map(str, line)) for line in array)


def calculateAngle(arrConnFaces,mesh):
	faceIdx0 = arrConnFaces.GetValue(0)
	faceIdx1 = arrConnFaces.GetValue(1)

	faceNorm0 = mesh.FaceNormals.Item[faceIdx0]
	faceNorm1 = mesh.FaceNormals.Item[faceIdx1]

	return rs.VectorAngle(faceNorm0,faceNorm1) #returns None on error



def generateMesh(rawNodes,faces):
	mesh = Rhino.Geometry.Mesh()
	for node in rawNodes:
		mesh.Vertices.Add(node[0],node[1],node[2])
	for face in faces:
		mesh.Faces.AddFace(face[0],face[1],face[2])

	mesh.UnifyNormals()
	mesh.Normals.ComputeNormals()
	mesh.Compact()
	mesh_id = scriptcontext.doc.Objects.AddMesh(mesh)
	if mesh_id !=System.Guid.Empty:
		scriptcontext.doc.Views.Redraw()
		return mesh_id,mesh
	return Rhino.Commands.Result.Failure


class Node():
	hasBeenCenter = False
	def __init__(self,coord,neighbors,edges):
		self.coord = coord
		self.X = coord[0]
		self.Y = coord[1]
		self.Z = coord[2]
		self.neighbors = neighbors
		self.edges = edges

	def draw(self):
		rs.AddPoint(self.X,self.Y,self.Z)

def getTriangleCoords(nodes):
	# this is the clique problem!
	polylineCoords = []
	faces = []
	for i, node in enumerate(nodes):
		edges = node.edges
		node.hasBeenCenter = True

		touchedNeighbors = []
		for neighIdx in node.neighbors:
			node2 = nodes[neighIdx]
			touchedNeighbors.append(neighIdx)

			if(not node2.hasBeenCenter):
				for nnIdx in node2.neighbors:
					node3 = nodes[nnIdx]

					if(not node3.hasBeenCenter and nnIdx not in touchedNeighbors):				
						if nnIdx in node.neighbors and nnIdx!=i:
							polylineCoords.append([node.coord,node2.coord,node3.coord,node.coord])
							faces.append([i,neighIdx,nnIdx])
	

	return polylineCoords, faces

def removeDups(list2D):
	#stackoverflow.com/questions/2213923/python-removing-duplicates-from-a-list-of-lists
	return list(k for k,_ in itertools.groupby(list2D))


def createGraph(rawNodes,rawEdges):
	nodes = []
	for i, coord in enumerate(rawNodes):
		#print i 
		neighbors,edges = findNeighbors(i,rawEdges)
		#if neighbors:
		node = Node(coord,neighbors,edges)
		nodes.append(node)
	return nodes

def findNeighbors(i,rawEdges):
	neighbors = []
	edges = []
	for edge in rawEdges:
		if(i in edge):
			edges.append(edge)
			idx = edge.index(i)
			#print(idx)
			if (idx == 0):
				neighbors.append(edge[1])
			elif (idx ==1):
				neighbors.append(edge[0])
	return neighbors,edges

test_rawEdges = [[1,2],[3,4],[2,4],[1,5],[2,100]]
tNeighbors,tEdges = findNeighbors(1,test_rawEdges)
assert(tNeighbors==[2,5] and tEdges==[[1,2],[1,5]]), "problem in findNeighbors"
#print(test_neighbors)






if __name__=="__main__":
	unwrapper()