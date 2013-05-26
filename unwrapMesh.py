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
	faces,edge_weights,thetaMax = getDual(mesh)
	displayDual(faces,edge_weights,thetaMax,mesh)

	foldList = getSpanningKruskal(faces,edge_weights,mesh)
	displayCutEdges(foldList,mesh)
	#displayNormals(mesh)

	


	print('Version:')
	print(sys.version )

def displayNormals(mesh):
	normLines = []
	for i in range(mesh.FaceNormals.Count):
		p1 = mesh.Faces.GetFaceCenter(i)
		p2 = p1 + mesh.FaceNormals.Item[i]
		normLines.append(rs.AddLine(p1,p2))
	createGroup("normLines",normLines)
"""
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
"""

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

"""THIS SHIT DOES NOT MAKE SENSE FOR THIS!!
def getSpanningPrimAlgo(faces,edge_weights,mesh):
	nFaces = len(faces)
	minSpanningTree = []
	viewEdges = []
	count = 0
	while count<nFaces:
		edgeIdx = None
		if count ==0:
			faceIdx = random.randint(0,nFaces-1)
		print "faceIdx:%d"%faceIdx
		#medges = mesh-edges
		conn_medges = mesh.TopologyEdges.GetEdgesForFace(faceIdx)
		medge_set = []
		for i in range(conn_medges.Length):
			medge_set.append(conn_medges.GetValue(i))
		#print medge_set
		medge_idxs = sorted(medge_set,key=lambda x:edge_weights[x])
		for possibleIdx in medge_idxs:
			if(possibleIdx not in minSpanningTree):
				edgeIdx = possibleIdx
				break
		minSpanningTree.append(edgeIdx)
		viewEdges.append(addLineForTEdge(edgeIdx,mesh))
		connFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIdx)

		if(connFaces.GetValue(0)==faceIdx):
			faceIdx = connFaces.GetValue(1)
		else:
			faceIdx = connFaces.GetValue(0)

		count +=1
	print str(len(viewEdges))
	createGroup("cutEdges",viewEdges)
"""



def getSpanningKruskal(faces,edge_weights,mesh):
	#note: have not considered open mesh, or non-manifold edges
	#input:
	#	faces = list of faces in mesh. necessary?
	#	edge_weights = list of tuples elem0 = edgeIdx, elem1 = weight
	#output:
	#	foldList = list of edgeIdx's that are to be cut
	treeSets = []
	foldList = []
	for tupEdge in edge_weights:
		edgeIdx = tupEdge[0]
		arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIdx)
		setConnFaces = set([arrConnFaces.GetValue(0),arrConnFaces.GetValue(1)])


		parentSets = []
		#print"edgeSet:"
		#print setConnFaces
		isLegal = True
		for i, treeSet in enumerate(treeSets):
			if setConnFaces.issubset(treeSet):
				#print"--was illegal"
				isLegal = False
				break
			elif not setConnFaces.isdisjoint(treeSet):
					#print"overlapped"
					parentSets.append(i)
			else:
				pass
				#print"not subset, isdisjoint"

		if isLegal==True:
			foldList.append(edgeIdx)
			if len(parentSets) == 0:
				treeSets.append(setConnFaces)
			elif len(parentSets) == 1:
				treeSets[parentSets[0]].update(setConnFaces)
			elif len(parentSets) == 2:
				treeSets[parentSets[0]].update(treeSets[parentSets[1]])
				treeSets.pop(parentSets[1])
			elif len(parentSets)>2:
				print"Error in m.s.t: more than two sets overlapped with edgeSet!"
				print "len parentSets: %d\n" %len(parentSets)
				print(treeSets)
				print(parentSets)
				print(setConnFaces)
				

		# wow there must be a cleaner way of doing this!!! some set tricks
		# also the if staements could be cleaned up probs.
	return foldList


def displayFoldEdges(foldList,mesh):
	foldLines = []
	for edgeIdx in foldList:
		foldLines.append(addLineForTEdge(edgeIdx,mesh))
	createGroup("foldLines",foldLines)

def displayCutEdges(foldLines,mesh):
	cutLines = []
	for i in range(mesh.TopologyEdges.Count):
		if i not in foldLines:
			cutLines.append(addLineForTEdge(i,mesh))
	createGroup("cutLines",cutLines)

def getKeyForMaxVal(edge_weights,medge_set):
	pass

def addLineForTEdge(edgeIdx,mesh):
	tVerts = mesh.TopologyEdges.GetTopologyVertices(edgeIdx)
	p1 = mesh.TopologyVertices.Item[tVerts.I]
	p2 = mesh.TopologyVertices.Item[tVerts.J]
	return rs.AddLine(p1,p2)



def getDual(mesh):
	#input: 
	#	mesh
	#ouput:
	#	faces = list of Faces as MeshFace class (4.rhino3d.com/5/rhinocommon/)
	#	connFaces = list of tuples (edgeIdx,weight)
	faces = []
	thetaMax = -1
	for i in range(mesh.Faces.Count):
		faces.append(mesh.Faces.GetFace(i))
	edge_weights = []
	for i in range(mesh.TopologyEdges.Count):
		arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(i)

		f0 = arrConnFaces.GetValue(0)
		f1 = arrConnFaces.GetValue(1)
		angWeight = calculateAngle(arrConnFaces,mesh)
		if angWeight > thetaMax:
			thetaMax = angWeight
		edge_weights.append((i,angWeight))
		#connFaces.append(tupleConnFaces)
	edge_weights = sorted(edge_weights,key=lambda tup: tup[1],reverse=False)
	#how to reverse order of sorting??

	
	pretty2DListPrint(edge_weights)

	return faces,edge_weights,thetaMax

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