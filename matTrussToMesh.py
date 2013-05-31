import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System


def importTrussData(nodesFileName=None,edgesFileName=None):
	rawNodes = getRawNodes(nodesFileName)
	rawEdges = getRawEdges(edgesFileName)
	return rawNodes,rawEdges


def constructMesh(rawNodes,rawEdges):
	nodes = createGraph(rawNodes,rawEdges)

	faces,polylineCoords = getTriangleCoords(nodes)
	#polyline coords is not being used, but could be useful later

	mesh, mesh_id = generateMesh(rawNodes,faces)
	# if faile to add to doc, mesh_id is going to be some number

	return mesh, mesh_id

def getRawNodes(fileName='data/trussNodes.csv'):
	nodeLines = importCsvFile(fileName)
	rawNodes = []

	for line in nodeLines:
		tokens = line.split(',')
		pnt = [float(item) for item in tokens]
		#rs.AddPoint( pnt)
		rawNodes.append(pnt)
	return rawNodes

def getRawEdges(fileName='data/trussEdges.csv'):
	edgeLines = importCsvFile(fileName)
	rawEdges = []

	for line in edgeLines:
		tokens = line.split(',')
		edge = [int(item) for item in tokens]
		idx1 = edge[0]-1 #matlab is 1-indexed!
		idx2 = edge[1]-1
		rawEdges.append([idx1,idx2])
	return rawEdges

def importCsvFile(fileName):
	csvFile = open(fileName,'rb')
	lines = csvFile.readlines()
	csvFile.close()
	return lines

def generateMesh(rawNodes,faces):
	'''
	input:	rawNodes = list [nNodes x 3] 3d pnts. imported from matlab-generated csv file
			faces = list [nFaces x 3] 3 indices into rawNodes that set a face
	output:	mesh_id = identifier of mesh object which has been added to document
			mesh = instance of Rhino.Geometry.Mesh()
			if faield to add mesh to the document: see Rhino.Commands Result Enumeration
	'''
	mesh = Rhino.Geometry.Mesh()
	for node in rawNodes:
		mesh.Vertices.Add(node[0],node[1],node[2])
	for face in faces:
		mesh.Faces.AddFace(face[0],face[1],face[2])

	mesh.UnifyNormals()
	mesh.Normals.ComputeNormals()
	mesh.Compact()
	mesh_id = scriptcontext.doc.Objects.AddMesh(mesh)
	if mesh_id != System.Guid.Empty:
		scriptcontext.doc.Views.Redraw()
		return mesh, mesh_id
	return mesh, Rhino.Commands.Result.Failure

def getTriangleCoords(nodes):
	'''this is the clique problem!
	input: nodes = list of instances of Node class: .Coord, .X, .Y, .Z, .neighbors, .edges
	output: polylineCoords = list [nTriangles x 4]: 4 pnts to set closed polyline <-not using
			faces = list [nFaces x 3] 3 indices into node list that determine a face. direction arbitrary
	'''
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


	return faces,polylineCoords

def createGraph( rawNodes, rawEdges):
	nodes = []
	for i, coord in enumerate(rawNodes):
		#print i
		neighbors,edges = findNeighbors(i,rawEdges)
		#if neighbors:
		node = Node(coord,neighbors,edges)
		nodes.append(node)
	return nodes

def findNeighbors( nodeIdx, rawEdges):
	neighbors = []
	edges = []
	for edge in rawEdges:
		if( nodeIdx in edge):
			edges.append( edge )
			idx = edge.index( nodeIdx )
			#print(idx)
			if (idx == 0):
				neighbors.append(edge[1])
			elif (idx ==1):
				neighbors.append(edge[0])
	return neighbors,edges

test_rawEdges = [[1,2],[3,4],[2,4],[1,5],[2,100]]
tNeighbors,tEdges = findNeighbors(1,test_rawEdges)
assert(tNeighbors==[2,5] and tEdges==[[1,2],[1,5]]), "problem in findNeighbors"


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





