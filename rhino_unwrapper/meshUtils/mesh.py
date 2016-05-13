import visualization as vis
import rhino_helpers as helpers
import transformations as trans
reload(vis)
reload(helpers)

import scriptcontext
import rhinoscriptsyntax as rs
import Rhino.Geometry as geom
import System
import clr

def make_test_mesh():
    '''
    returns an instance of myMesh and adds the rhinoMesh to the document
    '''
    vertices = []
    vertices.append((0.0,0.0,0.0))
    vertices.append((5.0, 0.0, 0.0))
    vertices.append((10.0, 0.0, 0.0))
    vertices.append((0.0, 5.0, 0.0))
    vertices.append((5.0, 5.0, 0.0))
    vertices.append((10.0, 5.0, 0.0))
    vertices.append((0.0, 10.0, 0.0))
    vertices.append((5.0, 10.0, 0.0))
    vertices.append((10.0, 10.0, 0.0))
    faceVertices = []
    faceVertices.append((0,1,4,4))
    faceVertices.append((2,4,1,1))
    faceVertices.append((0,4,3,3))
    faceVertices.append((2,5,4,4))
    faceVertices.append((3,4,6,6))
    faceVertices.append((5,8,4,4))
    faceVertices.append((6,4,7,7))
    faceVertices.append((8,7,4,4))
    return get_myMesh(vertices,faceVertices)

def make_upright_mesh():
    verts = []
    verts.append((0.0,0.0,0.0))
    verts.append((5.0,0.0,0.0))
    verts.append((5.0,0.0,5.0))
    verts.append((0.0,0.0,5.0))
    face_verts = []
    face_verts.append((0,1,3,3))
    face_verts.append((1,2,3,3))
    return get_myMesh(verts,face_verts)

def make_cube_mesh():
    vertices = []
    vertices.append((0.0,0.0,0.0)) #0
    vertices.append((5.0,0.0,0.0)) #1
    vertices.append((5.0,5.0,0.0)) #2
    vertices.append((0.0,5.0,0.0)) #3
    vertices.append((0.0,0.0,5.0)) #4
    vertices.append((5.0,0.0,5.0)) #5
    vertices.append((5.0,5.0,5.0)) #6
    vertices.append((0.0,5.0,5.0)) #7
    faceVertices = []
    faceVertices.append((3,2,1,0)) #bottom face
    faceVertices.append((4,5,6,7)) #top face
    faceVertices.append((0,1,5,4)) #front face
    faceVertices.append((4,7,3,0)) #left face
    faceVertices.append((1,2,6,5)) #right face
    faceVertices.append((2,3,7,6)) #back face
    return get_myMesh(vertices,faceVertices)


def get_myMesh(vertices,face_vertices):
    '''add a mesh to doc and get the Rhino.Geometry.Mesh object''' 
    mesh_GUID = rs.AddMesh( vertices, face_vertices )
    obj = scriptcontext.doc.Objects.Find(mesh_GUID)
    return Mesh(obj.Geometry)

#NOTE: even more hierarchical:
# Mesh.
#     .elements
#     .display
#     .select
#     .unfold <=!?

#NOTE: what if did something like:
# Mesh.
#     .vertexQuiery
#     .edgeQuiery
#     .faceQuiery
#     .special

#or mabe:
# mesh.Vertices
# mesh.Edges
# mesh.Faces
# mesh.Special
# ex: mesh.Vertices.get_
# ex: mesh.Speical.get_frame_asdfsdf()


class Mesh(object): 
    """
    better names?
    MeshQuieryer
    MeshFinder
    MeshElementFinder
    MeshElementGetter
    PythonMesh
    MyMesh

    Does custom queiries on a Rhino mesh that make layout easy
    see http://4.rhino3d.com/5/rhinocommon/ for rhino mesh class members
    - queries
    - visualizing info
    """

    def __init__(self,mesh):
        self.mesh = mesh
        self.mesh.FaceNormals.ComputeFaceNormals()
        self.cut_key = 'cuts'
        self.set_cuts([])

    ### GENERAL

    def edge_indices(self):
        pass

    def face_indices(self):
        return range(self.mesh.Faces.Count)

    def get_set_of_edges(self):
        count = self.mesh.TopologyEdges.Count
        return set(range(count))

    def get_set_of_face_idxs(self):
        return set(self.face_indices())

    def get_mesh_faces(self):
        """
        returns list of MeshFace instances that make up mesh
        """
        return (self.mesh.Faces.GetFace(i) for i in xrange(self.mesh.Faces.Count))

    def meshTVerts(self):
        return xrange(self.mesh.TopologyVertices.Count)

    ### SPECIAL, ie requires more than one extra index

    def get_frame_oriented_with_face_normal(self,edge,face):
        '''
        an edge and a face (meshLoc) imply a unique frame, 
        since the edge can be oriented according the the face's normal (right hand rule)
        '''
        face_edges = self.getFaceEdges(face)
        assert (edge in face_edges), "edge {} not in face {}".format(edge,face)
        basePoint,endPoint = self.get_oriented_points_for_edge(edge,face)
        normal = self.get_face_normal(face)
        xVec = helpers.getVectorForPoints(basePoint,endPoint)
        return trans.Frame.create_frame_from_normal_and_x(basePoint,normal,xVec)

    def getOtherFaceIdx(self,edgeIdx, faceIdx):
        connectedFaces = self.getFacesForEdge(edgeIdx)
        assert(faceIdx in connectedFaces), "faceIdx not in faces associated with edge"

        if len(connectedFaces) != 2:
            # This is a naked edge
            #print("did not find two connected faces for edgeIdx %i, " %(edgeIdx))
            return None

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

    ### QUIRED OBJECT IS VERTEX

    def get_point_for_tVert(self,tVert):
        '''
        Note: convertes Point3f to Point3d!
        '''
        return geom.Point3d(self.mesh.TopologyVertices.Item[tVert])

    def get_point3f_for_tVert(self,vert):
        return self.mesh.TopologyVertices.Item[vert]

    def getTVertsForVert(self,tVert):
        arrTVerts = self.mesh.TopologyVertices.ConnectedTopologyVertices(tVert)
        listVerts = vis.convertArray(arrTVerts)
        if tVert in listVerts:
            listVerts = listVerts.remove(tVert)
        return listVerts

    def getEdgesForVert(self,tVert):
        # not implimented in rhinoCommon! ::::(
        # rather inefficient
        neighVerts = self.getTVertsForVert(tVert)
        facesVert = set(self.getFacesForVert(tVert))
        edges = []
        for neighVert in neighVerts:

            edge = self.get_edge_for_vert_pair(tVert, neighVert)
            if edge:
                edges.append(edge)
        return edges

    def get_edge_for_vert_pair(self,vertA,vertB):
        return self.mesh.TopologyEdges.GetEdgeIndex(vertA,vertB)

    def getEdgeForTVertPair(self,tVertA, tVertB, facesVertA=None):
        ''' Depricated, use get_edge_for_vert_pair() '''
        if facesVertA is None:
            facesVertA = self.getFacesForVert(tVertA)
        facesVertB = set(self.getFacesForVert(tVertB))
        facePair = list(facesVertA.intersection(facesVertB))
        if len(facePair) == 2:
            edgesA = set(self.getFaceEdges(facePair[0]))
            edgesB = set(self.getFaceEdges(facePair[1]))
            edge = edgesA.intersection(edgesB)
            if len(edge) == 0:
                print "probably encountered naked edge in chain selection"
                return
            return list(edge)[0]
        elif len(facePair) == 1:
            # naked edge
            edges = self.getFaceEdges(facePair[0], self.mesh)
            for edge in edges:
                tVerts = self.getTVertsForEdge(edge)
                if tVertB in tVerts and tVertA in tVerts:
                    return edge
        return      

    def getFacesForVert(self,tVert):
        arrfaces = self.mesh.TopologyVertices.ConnectedFaces(tVert)
        return vis.convertArray(arrfaces)
    
    def getOtherTVert(self,edge, tVert):
        tVerts = self.getTVertsForEdge(edge)
        tVerts.remove(tVert)
        return tVerts[0]

    ### SPECIAL EDGE
    def get_aligned_points(self,orientedEdge):
        '''
        get points ordered according to orientation 
        '''
        edge, aligned_with_face = orientedEdge
        points = self.getPointsForEdge(edge)
        if not aligned_with_face:
            points.reverse()
        return points

    ### STUFF FOR LAYOUT

    def set_cuts(self,cutList):
        edges = self.get_set_of_edges()
        assert (edges.issuperset(set(cutList))), "cutList {} was not a subset of mesh edges".format(cutList)
        did_set = self.mesh.UserDictionary.Set(self.cut_key, System.Array[int](cutList))
        return did_set

    def get_cuts(self):
        return list(self.mesh.UserDictionary[self.cut_key])

    def is_cut_edge(self,edge):
        return edge in self.get_cuts()

    def is_fold_edge(self,edge):
        return edge not in self.get_cuts() and not self.is_naked_edge(edge)

    def is_naked_edge(self,edge):
        faces = self.getFacesForEdge(edge)
        nFaces = len(faces)
        assert (nFaces >0), "did not get any faces for edge {}".format(edge)
        if nFaces== 1:
            return True
        return False

    ### Main OBJECT IS EDGE

    def getTangentEdge(self,edge, tVert, angleTolerance, chain):
        '''
        return edge that is closest in angle, or none if none
        of the edges are within angleTolerance
        '''
        edges = self.getEdgesForVert( tVert)
        if edge in edges:
            edges.remove(edge)
        winEdge = (None, angleTolerance)
        for neighEdge in edges:
            angle = self.compareEdgeAngle(edge, tVert, neighEdge)
            if angle < angleTolerance and angle < winEdge[1]:
                winEdge = (neighEdge, angle)

        newEdge = winEdge[0]
        if newEdge is None:
            return chain
        if newEdge in chain:
            return chain
        else:
            chain.append(newEdge)
            nextTVert = self.getOtherTVert( newEdge, tVert)
            return self.getTangentEdge(newEdge, nextTVert, angleTolerance, chain)

    def getChain(self,edge, angleTolerance):
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

    def getFacesForEdge(self,edge):
        '''
        returns an array of indices of the faces connected to a given edge
        if the array has only one face this indicates it is a naked edge
        '''
        return list(self.mesh.TopologyEdges.GetConnectedFaces(edge))

    def getTVertsForEdge(self,edge):
        vertPair = self.mesh.TopologyEdges.GetTopologyVertices(edge)
        return [vertPair.I, vertPair.J]

    def getEdgeAngle(self,edge):
        '''
        get dihedral angle of a given edge in the mesh
        '''
        faceIdxs = self.getFacesForEdge(edge)
        if (len(faceIdxs)==2):
            faceNormA = self.mesh.FaceNormals.Item[faceIdxs[0]]
            faceNormB = self.mesh.FaceNormals.Item[faceIdxs[1]]
            return geom.Vector3d.VectorAngle(faceNormA,faceNormB)
        else:
            pass

    def getDistanceToEdge(self,edge, point):
        '''
        edge = Topology edgeIdx in mesh
        point = Point3d to get distance to edge
        '''
        edgeLine = self.mesh.TopologyEdges.EdgeLine(edge)
        return edgeLine.DistanceTo(point, True)

    def getEdgeVector(self,edgeIdx): 
        edgeLine = self.mesh.TopologyEdges.EdgeLine(edgeIdx)
        # Vector3d
        vec = edgeLine.Direction
        return vec
    
    def get_edge_vec_oriented(self,edgeIdx,faceIdx):
        tVerts = self.get_oriented_TVerts_for_edge(edgeIdx,faceIdx)
        pntA,pntB = self._get_points_for_tVerts(tVerts)
        return helpers.getVectorForPoints(pntA,pntB)

    def get_oriented_points_for_edge(self,edgIdx,faceIdx):
        tVerts = self.get_oriented_TVerts_for_edge(edgIdx,faceIdx)
        return self._get_points_for_tVerts(tVerts)

    def _get_points_for_tVerts(self,verts):
        points = []
        for vert in verts:
            points.append(self.mesh.TopologyVertices.Item[vert])
        return points

    def getPointsForEdge(self,edgeIdx):
        tVertI, tVertJ = self.getTVertsForEdge(edgeIdx)
        pntI = self.mesh.TopologyVertices.Item[tVertI]
        pntJ = self.mesh.TopologyVertices.Item[tVertJ]
        return [pntI, pntJ]
     
    def get_oriented_TVerts_for_edge(self,edgeIdx,faceIdx):
        """
        using the right-hand rule for face normals, each edge has a specific
        direction, given one of its ajoining faces. Returns the TVerts of that
        edge in that order.
        """
        correct_list = self.getTVertsForFace(faceIdx)
        edge_IJ = self.getTVertsForEdge(edgeIdx)
        assert set(edge_IJ).issubset(set(correct_list)), \
        "edge {} does not belong to face {}".format(edgeIdx,faceIdx)
        ordered_IJ = sorted(edge_IJ,key=lambda x:correct_list.index(x))
        if ordered_IJ[0]== correct_list[0] and ordered_IJ[-1] == correct_list[-1]:
            ordered_IJ.reverse()
        return ordered_IJ

    def get_edge_line(self,edgeIdx):
        return self.mesh.TopologyEdges.EdgeLine(edgeIdx)
    
    def getEdgeLen(self,edgIdx):
        edgeLine = self.get_edge_line(edgeIdx)
        return edgeLine.Length
    
    def get_edge_center_point(self,edgeIdx):
        line = self.get_edge_line(edgeIdx)
        cenX = (line.FromX + line.ToX) / 2.0
        cenY = (line.FromY + line.ToY) / 2.0
        cenZ = (line.FromZ + line.ToZ) / 2.0
        point =  geom.Point3d(cenX, cenY, cenZ)
        return point

    def compareEdgeAngle(self,edge, tVert, neighEdge):
        vecBase = self._getOrientedVector(edge, tVert, True)
        vecCompare = self._getOrientedVector(neighEdge, tVert, False)
        angle = geom.Vector3d.VectorAngle(vecBase, vecCompare)
        return angle

    def _getOrientedVector(self,edgeIdx, tVert, isEnd):
        '''
        tVert is the end point of this vector
        '''
        tVerts = self.getTVertsForEdge(edgeIdx)
        assert(tVert in tVerts)
        tVerts.remove(tVert)
        otherVert = tVerts[0]
        if isEnd:
            pntB = self.mesh.TopologyVertices.Item[tVert]
            pntA = self.mesh.TopologyVertices.Item[otherVert]
        else:
            pntA = self.mesh.TopologyVertices.Item[tVert]
            pntB = self.mesh.TopologyVertices.Item[otherVert]
        vecPnt = pntB - pntA
        vec = geom.Vector3d(vecPnt)
        return vec

    def getEdgeLengths(self):
        edgeLens = []
        for i in range(self.mesh.TopologyEdges.Count):
            edgeLine = self.mesh.TopologyEdges.EdgeLine(i)
            edgeLen = edgeLine.Length
            edgeLens.append(edgeLen)
        return edgeLens

    def getMedianEdgeLen(self):
        edgeLens = self.getEdgeLengths(self.mesh)
        return getMedian(edgeLens)

    ### Main OBJECT IS FACE
    def get_adjacent_faces(self,faceIdx):
        return list(self.mesh.Faces.AdjacentFaces(faceIdx))

    def getTVertsForFace(self,faceIdx):
        '''
        list of 4 values if quad, 3 values if triangle
        '''
        arrTVerts = self.mesh.Faces.GetTopologicalVertices(faceIdx)
        tVerts = list(arrTVerts)
        return helpers.uniqueList(tVerts)
    
    def get_points_for_face(self,faceIdx):
        '''
        Note: converts TopologyVertices as Point3f to Point3d
        '''
        tVerts = self.getTVertsForFace(faceIdx)
        points = []
        for tVert in tVerts:
            points.append(geom.Point3d(self.mesh.TopologyVertices.Item[tVert]))
        return points

    def getFaceEdges(self,faceIdx):
        arrFaceEdges = self.mesh.TopologyEdges.GetEdgesForFace(faceIdx)
        return list(arrFaceEdges)

    def get_edges_ccw_besides_base(self,baseEdge=None,face=None):
        '''
        get the edges for the face, except the baseEdges, ordered
        ccw around face, startin with the edge after the baseEdge
        '''
        #TODO: do assertion check that baseEdge belongs to the face
        edges,orientations = self.get_edges_and_orientation_for_face(face)
        index = edges.index(baseEdge)
        edges = helpers.rotate_and_remove(edges,index)
        orientations = helpers.rotate_and_remove(orientations,index)
        return zip(edges,orientations)

    def get_edges_and_orientation_for_face(self,faceIdx):
        orientations = clr.StrongBox[System.Array[bool]]()
        edges =  self.mesh.TopologyEdges.GetEdgesForFace(faceIdx,orientations)
        edges = list(edges)
        orientations = list(orientations.Value)
        #edges_with_orientations = zip(edges,orientations)
        return edges,orientations

    def get_edges_except(self,faceIdx,edgeIdx):
        face_edges = self.getFaceEdges(faceIdx)
        return face_edges.remove(edgeIdx)

    def get_face_normal(self,face):
        '''
        rhinocommon returns Vector3f, but most other rhioncommon
        stuff uses vector3d, so returns vector3d
        '''
        return geom.Vector3d(self.mesh.FaceNormals.Item[face])

class MeshDisplayer(object):

    def __init__(self,meshElementFinder):
        self.meshElementFinder = meshElementFinder

    def displayTVertsIdx(self):
        for vert in self.meshElementFinder.meshTVerts():
            self.displayTVertIdx(vert)

    def displayTVertIdx(self,vert, disp=None, color=(0, 255, 0, 255)):
        if disp is None:
           disp = vert
        point = self.meshElementFinder.mesh.TopologyVertices.Item[vert]
        vis.drawTextDot(point, str(disp), color)

    def displayEdgesIdx(self):
        for edge in self.meshElementFinder.get_set_of_edges():
            self.displayEdgeIdx(edge)

    def displayEdgeIdx(self,edgeIdx,color=(0,0,255,0)):
        point = self.meshElementFinder.get_edge_center_point(edgeIdx)
        return vis.drawTextDot(point, str(edgeIdx), color)

    def displayIJEdge(self, edgeIdx):
        pntI,pntJ = self.meshElementFinder.getPointsForEdge(edgeIdx)
        rs.AddTextDot('I', pntI)
        rs.AddTextDot('J', pntJ)

    def displayFacesIdx(self):
        for i,face in enumerate(self.meshElementFinder.get_set_of_face_idxs()):
            self.displayFaceIdx(i)

    def displayFaceIdx(self, face):
        centerPnt = self.meshElementFinder.mesh.Faces.GetFaceCenter(face)
        rs.AddTextDot(str(face), centerPnt)

    def displayNormals(self):
        normLines = []
        for i in range(self.meshElementFinder.mesh.FaceNormals.Count):
            pntCenter = self.meshElementFinder.mesh.Faces.GetFaceCenter(i)  # Point3d
            posVecCenter = geom.Vector3d(pntCenter)
            vecNormal = self.meshElementFinder.mesh.FaceNormals.Item[i]  # Vector3f
            vecNormal.Unitize()
            lineGuid = vis.drawVector(vecNormal, pntCenter)
            normLines.append(lineGuid)

    def display_face_vert_ordering(self,faceIdx):
        points = self.meshElementFinder.get_points_for_face(faceIdx)
        points.append(points[0])
        vis.drawPolyline(points,arrowType='end')

    def display_all_face_vert_ordering(self):
        faces = self.meshElementFinder.get_set_of_face_idxs()
        for face in faces:
            self.display_face_vert_ordering(face)

    def display_edge_direction_IJ(self,edgeIdx):
        pnts = self.meshElementFinder.getPointsForEdge(edgeIdx)
        vis.show_line_from_points(pnts,color=(0,0,0,255),arrowType='end')

    def display_all_edges_direction_IJ(self):
        for i in self.meshElementFinder.get_set_of_edges():
            self.display_edge_direction_IJ(i)
        
    def display_edge_direction(self,edgeIdx):
        line = self.meshElementFinder.get_edge_line(edgeIdx)
        vis.draw_arrow(line,color=(0,255,0,255))

    def display_all_edges_direction(self):
        for edge in self.meshElementFinder.get_set_of_edges():
            self.display_edge_direction(edge)

    def display_all_elements(self):
        self.displayFacesIdx()
        self.displayEdgesIdx()
        self.displayTVertsIdx()

    def display_edges(self, edgeIdxs,color=(0,255,0,255)):
        drawnEdges = {}
        if edgeIdxs:
            for edgeIdx in edgeIdxs:
                points = self.meshElementFinder.getPointsForEdge(edgeIdx)
                lineGuid, line = vis.show_line_from_points(points, color, 'none')
                drawnEdges[edgeIdx] = lineGuid
        return drawnEdges

if __name__ == "__main__":
    mesh = make_test_mesh()
    displayer = MeshDisplayer(mesh)
    displayer.display_all_elements()
    for i in mesh.get_set_of_face_idxs():
        print "face {} has edges: {}".format(i,mesh.getFaceEdges(i))
