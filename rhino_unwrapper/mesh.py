import Rhino

class Mesh(object):
    """
    Mesh is a class that keeps track of a rhino mesh specfically for unfolding
    """

    def __init__(self,mesh)
        self.mesh = mesh

    def getOtherFaceIdx(self,edgeIdx, faceIdx):
        connectedFaces = self.getFacesForEdge(self.mesh, edgeIdx)
        assert(faceIdx in connectedFaces), "faceIdx not in faces associated with edge"

        if len(connectedFaces) != 2:
            # This is a naked edge
            #print("did not find two connected faces for edgeIdx %i, " %(edgeIdx))
            return -1

        newFaceIdx = None
        if (connectedFaces[0] == faceIdx):
            newFaceIdx = connectedFaces[1]
        elif (connectedFaces[1] == faceIdx):
            newFaceIdx = connectedFaces[0]
        else:
            print "problem in getOtherFaceIdx: edgeIdx not in faceIdx,assert should have caught error"
            return None

        assert(newFaceIdx != faceIdx), "getOtherFaceIdx(): newFaceIdx == faceIdx!"
        return newFaceIdx

    def getTVertsForVert(tVert):
        arrTVerts = self.mesh.TopologyVertices.ConnectedTopologyVertices(tVert)
        listVerts = convertArray(arrTVerts)
        if tVert in listVerts:
            listVerts = listVerts.remove(tVert)
        return listVerts


    def getEdgesForVert(tVert):
        # not implimented in rhinoCommon! ::::(
        # rather inefficient
        neighVerts = self.getTVertsForVert(tVert)
        facesVert = set(self.getFacesForVert(self.mesh, tVert))
        edges = []
        for neighVert in neighVerts:

            edge = getEdgeForTVertPair(self.mesh, tVert, neighVert, facesVert)
            if edge:
                edges.append(edge)
        return edges

    def getEdgeForTVertPair(tVertA, tVertB, facesVertA=None):
        if facesVertA is None:
            facesVertA = self.getFacesForVert(self.mesh, tVertA)
        facesVertB = set(self.getFacesForVert(self.mesh, tVertB))
        facePair = list(facesVertA.intersection(facesVertB))
        if len(facePair) == 2:
            edgesA = set(self.getFaceEdges(facePair[0], self.mesh))
            edgesB = set(self.getFaceEdges(facePair[1], self.mesh))
            edge = edgesA.intersection(edgesB)
            if len(edge) == 0:
                print "probably encountered naked edge in chain selection"
                return
            return list(edge)[0]
        elif len(facePair) == 1:
            # naked edge
            edges = self.getFaceEdges(facePair[0], self.mesh)
            for edge in edges:
                tVerts = self.getTVertsForEdge(self.mesh, edge)
                if tVertB in tVerts and tVertA in tVerts:
                    return edge
        return      

    def getFacesForVert(tVert):
        arrfaces = self.mesh.TopologyVertices.ConnectedFaces(tVert)
        return convertArray(arrfaces)

    def getTVertsForEdge(edge):
        vertPair = self.mesh.TopologyEdges.GetTopologyVertices(edge)
        return [vertPair.I, vertPair.J]

    def getFacesForEdge(edgeIndex):
        '''
        returns an array of indices of the faces connected to a given edge
        if the array has only one face this indicates it is a naked edge
        '''
        arrConnFaces = self.mesh.TopologyEdges.GetConnectedFaces(edgeIndex)

        faceIdxs = []
        faceIdxs.append(arrConnFaces.GetValue(0))
        if arrConnFaces.Length == 2:
            faceIdxs.append(arrConnFaces.GetValue(1))

        return faceIdxs


    def getChain(edge, angleTolerance):
        '''
        gets chains extending from both ends of a given edge,
        using angleTolerance as stopping criterion
        '''
        chain = []
        tVerts = self.getTVertsForEdge(edge)
        for tVert in tVerts:
            subChain = self.getTangentEdge(edge, tVert, angleTolerance, [])
            chain.extend(subChain)
        chain.append(edge)
        return chain

    def getTangentEdge(edge, tVert, angleTolerance, chain):
        '''
        return edge that is closest in angle, or none if none
        of the edges are within angleTolerance
        '''
        edges = self.getEdgesForVert(self.mesh, tVert)
        if edge in edges:
            edges.remove(edge)
        winEdge = (None, angleTolerance)
        for neighEdge in edges:
            angle = self.compareEdgeAngle(self.mesh, edge, tVert, neighEdge)
            if angle < angleTolerance and angle < winEdge[1]:
                winEdge = (neighEdge, angle)

        newEdge = winEdge[0]
        if newEdge is None:
            return chain
        if newEdge in chain:
            return chain
        else:
            chain.append(newEdge)
            nextTVert = self.getOtherTVert(self.mesh, newEdge, tVert)
            return self.getTangentEdge(newEdge, nextTVert, angleTolerance, chain)

    def getOtherTVert(edge, tVert):
        tVerts = self.getTVertsForEdge(edge)
        tVerts.remove(tVert)
        return tVerts[0]

    def getDistanceToEdge(edge, point):
        '''
        edge = Topology edgeIdx in mesh
        point = Point3d to get distance to edge
        '''
        edgeLine = self.mesh.TopologyEdges.EdgeLine(edge)
        return edgeLine.DistanceTo(point, True)

    def getEdgeVector(edgeIdx):
        edgeLine = self.mesh.TopologyEdges.EdgeLine(edgeIdx)
        # Vector3d
        vec = edgeLine.Direction
        return vec

    def getPointsForEdge(edgeIdx):
        tVertI, tVertJ = self.getTVertsForEdge(self.mesh, edgeIdx)
        pntI = self.mesh.TopologyVertices.Item[tVertI]
        pntJ = self.mesh.TopologyVertices.Item[tVertJ]
        return [pntI, pntJ]
    
    def getEdgeLen(edgIdx):
        edgeLine = self.mesh.TopologyEdges.EdgeLine(edgeIdx)
        return edgeLine.Length

    def compareEdgeAngle(edge, tVert, neighEdge):
        vecBase = getOrientedVector(self.mesh, edge, tVert, True)
        vecCompare = getOrientedVector(self.mesh, neighEdge, tVert, False)
        angle = Rhino.Geometry.Vector3d.VectorAngle(vecBase, vecCompare)
        return angle

    def getEdgeLengths():
        edgeLens = []
        for i in range(self.mesh.TopologyEdges.Count):
            edgeLine = self.mesh.TopologyEdges.EdgeLine(i)
            edgeLen = edgeLine.Length
            edgeLens.append(edgeLen)
        return edgeLens

    def getMedianEdgeLen():
        edgeLens = self.getEdgeLengths(self.mesh)
        return getMedian(edgeLens)

    def getTVertsForFace(faceIdx):
        '''
        list of 4 values if quad, 3 values if triangle
        '''
        arrTVerts = self.mesh.Faces.GetTopologicalVertices(faceIdx)
        tVerts = convertArray(arrTVerts)
        return uniqueList(tVerts)

    def getFaceEdges(faceIdx):
        arrFaceEdges = self.mesh.TopologyEdges.GetEdgesForFace(faceIdx)
        return convertArray(arrFaceEdges)



