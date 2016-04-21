
class Map(object):
    """Map:a class for keeping track of the relation between the net and the mesh. Now that multiple islands form a net, the map needs to saw which island, and then which element index in the island. This sounds like a natural tuple or array with [islandIdx,elementIdx]. A mutable type makes sense since islands can be edited
    * at this moment it seems the only important objects to map are edges!
    """


    def __init__(self, myMesh):
        self.meshVerts = {}
        self.meshEdges = {}
        self.meshFaces = {}
        for i in xrange(myMesh.mesh.TopologyVertices.Count):
            self.meshVerts[i] = []
        for j in xrange(myMesh.mesh.TopologyEdges.Count):
            self.meshEdges[j] = []
        for faceIdx in xrange(myMesh.mesh.Faces.Count):
            self.meshFaces[faceIdx] = []

    def island_edge_already_added(self,island_edge):
        #if island_edge  
        pass

    def updateEdgeMap(self, edge, netEdge):
        '''To be called imediately after adding an edge'''
        self.meshEdges[edge].append(netEdge)

    def updateVertMap(self, tVert, netVert):
        self.meshVerts[tVert].append(netVert)
    
    def add_edge(self,meshEdge,islandIdx,islandEdge):
        ''' TBD '''
        pass

    def add_child_to_vert(self,tVert,childVert):
        self.meshVerts[tVert].append(childVert)

    def get_recent_island_vert(self,tVert):
        return self.meshVerts[tVert][-1]

    def getSiblingNetEdge(self, edge, netEdge):
        '''for a cut edge get the sibling edge'''
        edges = self.meshEdges[edge]
        netEdges = set(edges)
        netEdge = set([netEdge])
        singleEdge = netEdges - netEdge
        return singleEdge.pop()

    def getNetEdges(self, meshEdge):
        return self.meshEdges[meshEdge]

    def getRecentNetVertsForEdge(self, myMesh, edge):
        meshI, meshJ = myMesh.getTVertsForEdge(edge)
        netI = self.getRecentNetVert(meshI)
        netJ = self.getRecentNetVert(meshJ)
        return netI, netJ

    def getRecentNetVert(self, tVert):
        return self.meshVerts[tVert][-1]  # get last item in list
