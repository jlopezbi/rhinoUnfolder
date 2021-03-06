
#DEPRICATED
class IslandCreator(object):
    """DEPRICATED, left for now in case need to check how did something traverses a mesh to create an island """

    def __init__(self,dataMap=None,myMesh=None,mesh_loc=None,start_frame=None,island_index=None):
        self.dataMap = dataMap
        self.myMesh = myMesh
        self.mesh_loc = mesh_loc
        self.island_loc = IslandLoc(0,0,[0,1])
        self.island_index = island_index #index of island in net

        self.island = nt.Island()
        if start_frame==None:
            start_frame = trans.make_origin_frame()
        self.to_frame = start_frame
        self.update_from_frame()
        self.visualize_mode = True
        if self.visualize_mode:
            self.to_frame.show()
            self.from_frame.show()

    def make_island(self,foldList,mesh_frame,toBasis):
        self.foldList = foldList
        self.layout_face(None,None,mesh_frame,toBasis)

    def new_layout(self,meshLoc,islandLoc):
        self.add_facet_to_island_and_update_map(meshLoc,islandLoc) #does the map get updated in here. yes
        edges = self.myMesh.getFaceEdges(meshLoc.face)
        for edge in faceEdges:
            if self.is_fold(edge):
                self.modify_edge_type('fold',edge) #edge can now have meshEdgeIdx
                # RECURSE
                new_island_loc = self.get_new_island_loc(islandLoc,edge)
                new_mesh_loc = self.get_new_mesh_loc(meshLoc,edge)
                new_layout(new_mesh_loc,new_island_loc)
            if self.is_cut(edge):
                self.island.modify_edge_type('cut') #sibling edge found using map
            if self.is_naked(edge):
                self.island.modify_edge_type('naked')

    def update_from_frame(self):
        self.from_frame = trans.get_frame_on_mesh(self.mesh_loc,self.myMesh)

    def update_to_frame(self):
        if self.island_loc != None:
            face,edge = self.island_loc
            self.to_frame = self.island.get_frame_reverse_edge(face,edge)

    def add_first_edge_to_island(self):
        ''' first edge and verts added to island so that recursion is easier'''
        sourceFace,sourceEdge,sourceVert = self.mesh_loc
        edgePoints = self.myMesh.get_oriented_points_for_edge(sourceEdge,sourceFace)
        islandVertPair = []
        for point in edgePoints:
            mapped_point = trans.get_mapped_point(point,self.from_frame,self.to_frame)
            islandVertPair.append(self.island.add_vert_from_point(mapped_point))
        indexInFace = 0 #always will be first edge in face (?)
        face = 0 #always will be from first face
        island_edge = self.island.add_edge_with_from_face(0,index=indexInFace) 
        self.dataMap.add_edge(sourceEdge,self.island_index,island_edge)
        
# NEW PLAN:
# iterate edge-wise over edges for meshFace and  use GetEdgesForFace() method
# that outputs list of booleans for edges that are backwards relative to face
# then can add only the head vert for each edge
    
    def add_facet(self):
        self.update_from_frame()
        self.update_to_frame()
        sourceFace,sourceEdge,sourceVert = self.mesh_loc #indices
        islandFace,islandEdge,islandVertPair = self.island_loc #indices
        edges,orientations = self.myMesh.get_edges_and_orientation_for_face(sourceFace)
        for i,edge in enumerate(edges):
            if self.edge_not_added(edge):
                vert_list = self.myMesh.getTVertsForEdge(edge)
                point_list = self.myMesh.getPointsForEdge(edge)
                if not orientations[i]:
                    vert_list.reverse()
                    point_list.reverse()
                mapped_point = trans.get_mapped_point(point_list[1],self.from_frame,self.to_frame)
                self.island.add_vert_from_point(mapped_point)
                self.island.add_edge_before_face(i)
            else:
                pass

    def add_facet_to_island_and_update_map(self):
        self.update_from_frame()
        self.update_to_frame()
        sourceFace,sourceEdge,sourceVert = self.mesh_loc #indices
        islandFace,islandEdge,islandEdgeVerts = self.island_loc #indices
        edgeTVerts = set(self.myMesh.getTVertsForEdge(sourceEdge))
        all_verts = self.myMesh.getTVertsForFace(sourceFace)
        verts_to_assign = set(all_verts)
        if self.island_loc != None:
            verts_to_assign = verts_to_assign.difference(edgeTVerts)
        island_face_verts = []
        island_face_edges = []
        for i,vert in enumerate(all_verts):
            if vert in verts_to_assign:
                point = self.myMesh.get_point_for_tVert(vert)
                mapped_point = trans.get_mapped_point(point,self.from_frame,self.to_frame)
                new_island_vert = self.island.add_vert_from_point(mapped_point)
                self.dataMap.add_child_to_vert(vert,new_island_vert)
            next_vert = all_verts[ (i+1)%len(all_verts) ]
            island_vert = self.dataMap.get_recent_island_vert(vert)
            island_next_vert = self.dataMap.get_recent_island_vert(next_vert)
            island_face_verts.append(island_vert)
            #TODO: this is absurdely ugly (below line) need to figure out better organization to avoid
            island_hop_edge_verts = self.island.flatEdges[islandEdge].get_verts(self.island.flatVerts)
            if set([island_vert,island_next_vert]) != set(island_hop_edge_verts):
                new_edge_idx = self.island.add_edge_with_from_face(sourceFace,i)
                island_face_edges.append(new_edge_idx)
        flatFace = self.island.add_face_verts_edges(island_face_verts,island_edges)

    def layout_face(self, fromFace, hopEdge, meshLoc, to_frame):
        ''' Recursive Function to traverse through faces, hopping along fold edges
            input:
                fromface = 
                hopEdge = 
                meshLoc = (faceIdx,edgeIdx,tVertIdx) information required to make basis
                self.myMesh = a wrapper for RhinoCommon mesh, to unfold
                to_frame = frame in flat world
            out/in:
                flatEdges = list containing flatEdges (a class that stores the edgeIdx,coordinates)
        '''
        """FLAT VERTS"""
        new_island_verts = self.assign_flat_verts(meshLoc,to_frame,fromFace) 
        """FLAT FACES"""
        new_island_face = self.island.add_face(flatGeom.FlatFace(new_island_verts,fromFace))
        self.dataMap.meshFaces[meshLoc.face] = new_island_face

        """FLAT EDGES"""
        faceEdges = self.myMesh.getFaceEdges(meshLoc.face)
        for edge in faceEdges:
            meshI, meshJ = self.myMesh.getTVertsForEdge(edge)

            if edge in self.foldList:
                if not self.alreadyBeenPlaced(edge, self.dataMap.meshEdges):

                    new_mesh_frame = self.getNewBasisInfo(meshLoc, edge, self.myMesh)
                    edgeCoords = (self.island.flatVerts[netI].point,self.island.flatVerts[netJ].point)

                    flatEdge = fe.FoldEdge(meshEdgeIdx=edge, vertAidx=netI,
                                   vertBidx=netJ,fromFace=meshLoc.face,toFace=new_mesh_frame.face) 
                    netEdge = self.island.addEdge(flatEdge)
                    self.dataMap.updateEdgeMap(edge, netEdge)

                    # RECURSE
                    recurse = True
                    new_net_frame = trans.get_net_frame(edgeCoords)
                    self.dataMap = self.layout_face( meshLoc.face, flatEdge, new_mesh_frame,new_net_frame)

            else:
                if len(self.dataMap.meshEdges[edge]) == 0:
                    flatEdge = fe.FlatEdge(meshEdgeIdx=edge, vertAidx=netI,
                                   vertBidx=netJ,fromFace=meshLoc.face)
                    netEdge = self.island.addEdge(flatEdge)
                    self.dataMap.updateEdgeMap(edge, netEdge)

                elif len(self.dataMap.meshEdges[edge]) == 1:
                    otherEdge = self.dataMap.meshEdges[edge][0]
                    otherFace = self.myMesh.getOtherFaceIdx(edge,meshLoc.face)
                    flatEdge = fe.CutEdge(meshEdgeIdx=edge,
                                          vertAidx=netI,
                                          vertBidx=netJ,
                                          fromFace=meshLoc.face,
                                          toFace=otherFace,
                                          sibling=otherEdge)
                    flatEdge.get_other_face_center(self.myMesh, meshLoc.face, xForm)
                    netEdge = self.island.addEdge(flatEdge)
                    self.dataMap.updateEdgeMap(edge, netEdge)
                    sibFlatEdge = self.island.flatEdges[otherEdge]
                    self.island.flatEdges[otherEdge] = fe.change_to_cut_edge(sibFlatEdge,netEdge)

    def assign_flat_verts(self,meshLoc,to_frame,start=False):
        from_frame = trans.get_frame_on_mesh(meshLoc,self.myMesh)
        if self.visualize_mode:
            from_frame.show()
        faceIdx = meshLoc.face
        edgeIdx = meshLoc.edge
        edgeTVerts = set(self.myMesh.getTVertsForEdge(edgeIdx))
        verts_to_assign = set(self.myMesh.getTVertsForFace(faceIdx))
        if not start:
            verts_to_assign = verts_to_assign.difference(edgeTVerts)
        new_island_verts = []
        for vert in verts_to_assign:
            point = self.myMesh.get_point_for_tVert(vert)
            mapped_point = trans.get_mapped_point(point,from_frame,to_frame)
            new_island_vert = self.island.add_vert_from_point(mapped_point)
            new_island_verts.append(new_island_vert)
            self.dataMap.add_child_to_vert(vert,new_island_vert)
        return new_island_verts

    def assignFlatVerts(self, hopEdge, face, from_frame, to_frame):
        '''
        add valid flatVerts to flatVerts list and also return
        a list of netVertassignFlatVerts
        '''

        face_verts = self.myMesh.getTVertsForFace(face)
        netVerts = []
        hopMeshVerts = []

        if hopEdge is not None:
            netI, netJ = [hopEdge.vertAidx, hopEdge.vertBidx]
            hopMeshVerts = [
                self.island.flatVerts[netI].tVertIdx,
                self.island.flatVerts[netJ].tVertIdx]
            self.dataMap.add_child_to_vert(hopMeshVerts[0],netI)
            mapping[hopMeshVerts[0]] = netI
            mapping[hopMeshVerts[1]] = netJ

        for vert in face_verts:
            if vert not in hopMeshVerts:
                point = self.myMesh.get_point_for_tVert(vert)
                mapped_point = trans.get_mapped_point(point,from_frame,to_frame) 
                flatVert = flatGeom.FlatVert(vert, mapped_point)
                newVertIdx = self.island.addVert(flatVert)
                self.dataMap.meshVerts[point].append(newVertIdx)
                netVerts.append(flatVert)
                mapping[vert] = flatVert
            else:
                # this section is important for preserving order
                if vert == self.island.flatVerts[netI].tVertIdx:
                    netVerts.append(netI)
                elif point == self.island.flatVerts[netJ].tVertIdx:
                    netVerts.append(netJ)
        return netVerts, mapping

    def getNewBasisInfo(self, oldBasisInfo, testEdgeIdx, myMesh):
        faceIdx, edgeIdx, tVertIdx = oldBasisInfo
        newFaceIdx = myMesh.getOtherFaceIdx(testEdgeIdx, faceIdx)
        newEdgeIdx = testEdgeIdx
        newTVertIdx = myMesh.mesh.TopologyEdges.GetTopologyVertices(
            testEdgeIdx).I  # convention: useI
        return Basis(newFaceIdx, newEdgeIdx, newTVertIdx)

    def getNetEdges(self, mesh, edge, netVerts, dataMap):
        I, J = mesh.getTVertsForEdge(edge)
        vertI = dataMap.get

    def transformPoint(self, mesh, tVert, xForm):
        #NOTE: mesh.TopologyVertices.Item returns a point3f
        point = Rhino.Geometry.Point3d(mesh.TopologyVertices.Item[tVert])
        point.Transform(xForm)
        point.Z = 0.0  # TODO: find where error comes from!!! (rounding?)
        return point

    def edge_not_added(self, edge):
        return not self.dataMap.meshEdges[edge]
