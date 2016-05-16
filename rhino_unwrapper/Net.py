import rhino_helpers 
import flatGeom
import flatEdge
import Rhino
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs
import math
import transformations as trans
from UnionFind import UnionFind

reload(trans)
reload(flatGeom)
reload(flatEdge)


class Net():
    """ 
    What if Net was composed of islands?! each island has verts,edge and faces.
    What does a net do?, slash know about?
        => it stores the mesh that is the net. In fact perhaps should just use rhino's mesh! but lets save that for later
    Right now the net does this:
        * Segmentation <= this is the main thing!
            * Selection
        * Display

    Queries: (this will help determine best Data structure)
        * for a given edge its parent face and its otherParnet face (assuming a manifold edge)
        * for a given cut edge, its corresponding edge
        * for a given edge, the two sets of edges/faces/verts on either side, or for a given edge, the set of edges/faces/verts on the side indicated by the user (faster)
        non essential:
        * for a given edge, the corrseponding edge in the 3d mesh
    """
#myMesh.mesh.Faces.Count

    def __init__(self, myMesh, holeRadius=10):
        self.holeRadius = holeRadius
        self.angleThresh = math.radians(3.3)
        self.myMesh = myMesh
        self.islands = []
        #self.groups,self.leaders = segmentIsland(self.flatFaces,[])

    def add_island(self,island):
        self.islands.append(island)

    def display(self):
        for island in self.islands:
            island.display()


    def get_island_for_line(self,line_guid):
        # naively would iterate through each island and see if edge is in it.
        # another approach: see if it is in each island's bounding box (can have errors)
        # another: check if edge is inside island's perimeter (need to get island's perimeter)
        #NOTE: starting with naive option
        for island in self.islands:
            if line_guid in island.line_edge_map.keys():
                return island

    '''SEGMENTATION, seems like should be a seperate thing!'''
    #Now when segmentation happens a two new islands should be created
    #A new challenge is finding the island that owns the line or meshEdge that the user selected!
    #it seems like union find is not necessary when using island idea! whoa! but keep this code in case wrong
    def segment_island(self):
        pass

    def segmentIsland(flatFaces, island):
        sets = UnionFind(True)
        if len(island) == 0:
            island = range(len(flatFaces))
        for face in island:
            if face not in sets.leader.keys():
                sets.makeSet([face])
            neighbor = flatFaces[face].fromFace
            if neighbor is not None:
                if neighbor not in sets.leader.keys():
                    sets.makeSet([neighbor])
                sets.union(face, neighbor)
        return sets.group, sets.leader

    def findInitalSegments(self):
        group, leader = self.segmentIsland(self.flatFaces, [])
        self.groups = group
        self.leaders = leader

    def findSegment(self, flatEdgeCut, face):
        island = self.getGroupForMember(face)
        self.removeFaceConnection(flatEdgeCut)
        group, leader = self.segmentIsland(self.flatFaces, island)
        self.updateIslands(group, leader, face)
        return group[leader[face]]

    def getGroupForMember(self, member):
        if member not in self.leaders.keys():
            print "face not in leaders: ",
            print member
            return
        leader = self.leaders[member]
        return self.groups[leader]

    def updateIslands(self, newGroups, newLeaders, face):
        # get rid of old island
        leader = self.leaders[face]
        del self.groups[leader]

        for group in newGroups.items():
            self.groups[group[0]] = group[1]
        for leader in newLeaders.items():
            self.leaders[leader[0]] = leader[1]

    def copyAndReasign(self, dataMap, flatEdge, idx, segment, face):
        # TODO: this must change because of change to cut/fold edge types
        # GOT TO REWORK THIS ONE
        newEdgeIdx = len(self.flatEdges)
        resetEdge = fe.change_to_cut_edge(flatEdge,newEdgeIdx)
        resetEdge.resetFromFace(face)
        changedVertPairs = self.makeNewNetVerts(dataMap, flatEdge)
        newEdge = self.makeNewEdge(
            dataMap,
            changedVertPairs,
            flatEdge.meshEdgeIdx,
            idx,
            face,flatEdge.getOtherFace(face))
        flatEdge.pair = newEdge
        flatEdge.show_line(self.flatVerts)
        # flatEdge.drawHoles(self,connectorDist,safetyRadius,holeRadius)
        self.resetSegment(dataMap, changedVertPairs, segment)

    def translateSegment(self, segment, xForm):
        # TODO: make a more efficent version of this, would be easier if half-edge or
        # winged edge mesh. H-E: could traverse edges recursively, first going to sibling h-edge
        # Sstopping when the edge points to no other edge(naked),or to a face not in the segment,or
        # if the h-edge is part of the user-selected edge to be cut
        group = rs.AddGroup()
        collection = []
        movedNetVerts = []
        for netEdge in self.flatEdges:
            if netEdge.fromFace in segment:
                collection.append(netEdge)
                netEdge.clearAllGeom()
                netEdge.translateGeom(movedNetVerts, self.flatVerts, xForm)
        return collection

    def redrawSegment(self, translatedEdges):
        geom = []
        for netEdge in translatedEdges:
            netEdge.show_line(self.flatVerts)

    def removeFaceConnection(self, flatEdgeCut):
        faceA = flatEdgeCut.fromFace
        faceB = flatEdgeCut.toFace
        netFaceA = self.flatFaces[faceA]
        netFaceB = self.flatFaces[faceB]
        if netFaceB.fromFace == faceA:
            netFaceB.fromFace = None
        elif netFaceA.fromFace == faceB:
            netFaceA.fromFace = None

    def makeNewEdge(self, dataMap, changedVertPairs, meshEdge, otherEdge, fromFace,toFace):
        newVertI = changedVertPairs[0][0]
        newVertJ = changedVertPairs[1][0]
        newFlatEdge = fe.CutEdge(meshEdgeIdx=meshEdge,
                                 vertAidx=newVertI,
                                 vertBidx=newVertJ,
                                 fromFace=fromFace,
                                 toFace=toFace,
                                 sibling=otherEdge)
        newFlatEdge.hasTab = True
        newFlatEdge.tabFaceCenter = self.flatFaces[toFace].getCenterPoint(self.flatVerts)
        
        # This is where need to add a tabFaceCenter thing that will find the otherFace
        # of the edge and find its center
        # TODO: need to set tab angles or something. NOTE: .fromFace and
        # .toFace of flatEdge referes to a MESH face!!
        netEdge = self.addEdge(newFlatEdge)
        dataMap.updateEdgeMap(meshEdge, netEdge)
        return netEdge

    def makeNewNetVerts(self, dataMap, flatEdgeCut):
        oldNetI, oldNetJ = flatEdgeCut.getNetVerts()
        flatI, flatJ = flatEdgeCut.getFlatVerts(self.flatVerts)
        pointI = Rhino.Geometry.Point3d(flatI.point)  # important copy vert
        pointJ = Rhino.Geometry.Point3d(flatJ.point)
        newI = FlatVert(flatI.tVertIdx, pointI)
        newJ = FlatVert(flatJ.tVertIdx, pointJ)
        newNetI = self.addVert(newI)
        newNetJ = self.addVert(newJ)
        dataMap.updateVertMap(flatI.tVertIdx, newNetI)
        dataMap.updateVertMap(flatJ.tVertIdx, newNetJ)
        return [(newNetI, oldNetI), (newNetJ, oldNetJ)]

    def resetSegment(self, dataMap, changedVertPairs, segment):
        self.resetFaces(changedVertPairs, segment)
        self.resetEdges(dataMap, changedVertPairs, segment)

    def resetFaces(self, changedVertPairs, segment):
        # REPLACE: this is slow hack
        newVertI, oldVertI = changedVertPairs[0]
        newVertJ, oldVertJ = changedVertPairs[1]
        for face in segment:
            verts = self.flatFaces[face].vertices
            if oldVertI in verts:
                index = verts.index(oldVertI)
                verts.insert(index, newVertI)  # does order matter? yes
                verts.pop(index + 1)
            if oldVertJ in verts:
                index = verts.index(oldVertJ)
                verts.insert(index, newVertJ)  # does order matter? yes
                verts.pop(index + 1)

    def resetEdges(self, dataMap, changedVertPairs, segment):
        '''
        reset all edges touching the newely added vertices
        '''
        # REPLACE: if using he-mesh then this will be unnecessary
        for pair in changedVertPairs:
            newVert, oldVert = pair
            tVert = self.flatVerts[newVert].tVertIdx
            print "Tvert:",
            print tVert
            # in original mesh,eventually use he-mesh
            edges = self.myMesh.getEdgesForVert(tVert)
            for edge in edges:
                netEdges = dataMap.getNetEdges(edge)
                for netEdge in netEdges:
                    flatEdge = self.getFlatEdge(netEdge)
                    netPair = flatEdge.getNetVerts()
                    if oldVert in netPair and flatEdge.fromFace in segment:
                        #assert(flatEdge.fromFace in segment), "flatEdge not in segment"
                        flatEdge.reset(oldVert, newVert) 

class Island(object):

    def __init__(self):
        '''
        stores flatVerts,flatEdges and flatFaces and draws itself
        Random thought: each island could have a map 
        Yooo could have a class for each collection like planton..
        '''
        self.flatVerts = []
        self.flatEdges = []
        self.flatFaces = []  
        self.line_edge_map = {}
        self.temp_edges = []
        self.temp_verts = []
        self.debug_visualize = False

    def add_dummy_elements(self): 
        '''
        to be used for layout; initializes with edge and face
        '''
        self.dummyFace = self.add_face(flatGeom.FlatFace([0,1],[0]))
        self.dummyEdge = self.add_edge_with_from_face(face=0,index=0)

    #LAYOUT
    def change_to_fold_edge(self,edge):
        baseEdge = self.flatEdges[edge]
        self.flatEdges[edge] = flatEdge.create_fold_edge_from_base(baseEdge)

    #LAYOUT
    def change_to_cut_edge(self,edge):
        baseEdge = self.flatEdges[edge]
        self.flatEdges[edge] = flatEdge.create_cut_edge_from_base(baseEdge)

    #LAYOUT
    def change_to_naked_edge(self,edge):
        baseEdge = self.flatEdges[edge]
        self.flatEdges[edge] = flatEdge.create_naked_edge_from_base(baseEdge)

############ QUIERY
    def get_point_for_vert(self,vert):
        return self.flatVerts[vert].point

    def next_face_index(self):
        return len(self.flatFaces)

######### ADDING ELEMENTS    
    def tack_on_facet(self,edge,points):
        newFaceIdx = len(self.flatFaces)
        baseEdge = self.flatEdges[edge]
        baseEdge.toFace = newFaceIdx
        edge_verts = baseEdge.get_reversed_verts(self) 
        faceEdges = [edge]
        faceVerts = [edge_verts[0],edge_verts[1]]
        for i,point in enumerate(points):
            newVert = self.add_vert_from_point(point)
            newEdge = self.add_edge_with_from_face(newFaceIdx,i+1)
            faceVerts.append(newVert)
            faceEdges.append(newEdge)
        finalEdge = self.add_edge_with_from_face(newFaceIdx,len(points)+1)
        faceEdges.append(finalEdge)
        newFaceIdx = self.add_face_verts_edges(faceVerts,faceEdges)
        faceEdges.pop(0)  #only return new edges
        return newFaceIdx,faceEdges

################## ADD VERT
#LAYOUT
    def layout_add_vert_point(self,point):
        '''
        designed for layout: verts get added before face 
        '''
        vertIdx = self.add_vert(flatGeom.FlatVert(point))
        self.temp_verts.append(vertIdx)

    def add_new_points(self,points,edge):
        old_verts = self.flatEdges[edge].get_verts(self).reverse()

    def add_vert_from_points(self,x,y,z):
        return self.add_vert(flatGeom.FlatVert.from_coordinates(x,y,z))

    def add_vert_from_point(self,point):
        vertIdx = self.add_vert(flatGeom.FlatVert(point))
        return vertIdx

    def add_vert(self, flatVert):
        self.flatVerts.append(flatVert)
        return len(self.flatVerts) - 1

################## ADD EDGE

#LAYOUT
    def layout_add_edge(self,index=None):
        '''
        designed for layout: edge gets added before face gets added
        '''
        newFaceIdx = len(self.flatFaces)
        newEdge = self.add_edge(flatEdge.FlatEdge(fromFace=newFaceIdx,indexInFace=index))
        self.temp_edges.append(newEdge)
        return newEdge

    def update_edge_to_face(self,edge,toFace):
        edge_obj = self.get_edge_obj(edge)
        edge_obj.toFace = toFace

    def add_edge_with_from_face(self,face=None,index=None):
        edgeIdx =  self.add_edge(flatEdge.FlatEdge(fromFace=face,indexInFace=index))
        return edgeIdx

    def add_edge(self, flatEdge):
        self.flatEdges.append(flatEdge)
        return len(self.flatEdges) - 1

################## ADD FACE
#LAYOUT
    def layout_add_face(self,baseEdge):
        '''
        designed for layout: verts and edges are added before this function is called.
        Base edge is an edge index in this island that already exists.
        '''
        assert self.temp_verts, "temp_verts is empty, need to add verts first"
        assert self.temp_edges, "temp_edges is empty, need to add edges first"
        baseVerts = self.flatEdges[baseEdge].get_reversed_verts(self)
        verts = baseVerts + self.temp_verts
        edges = [baseEdge] + self.temp_edges
        face = self.add_face_verts_edges(verts,edges)
        self.temp_verts = []
        self.temp_edges = []
        if self.debug_visualize:
            face_obj = self.flatFaces[face]
            face_obj.draw(self)
            face_obj.show_index(face,self)
            for edge in face_obj.edges:
                self.flatEdges[edge].show_index(edge,self)
            
    def add_face_before(self,vertPair,nEdges):
        n_new_verts = nEdges-2
        first_new_vert = len(self.flatVerts)
        last_new_vert = first_new_vert + n_new_verts
        verts = vertPair + range(first_new_vert,last_new_vert)

    def add_face_from_recent(self,edge):
        already_placed_verts = self.flatEdges[edge].get_verts(self).reverse()
        verts = already_placed_verts + self.temp_verts
        edges = [edge] + self.temp_edges
        flatFace = flatGeom.FlatFace(verts,edges)
        self.temp_verts = []
        self.temp_edges = []
        return self.add_face(flatFace)

    def add_first_face_from_verts(self,*verts):
        '''any number of ordered vertex indices '''
        faceIdx_to_be = len(self.flatFaces)
        edges = []
        for i,vert in enumerate(verts):
            newEdgeIdx = self.add_edge_with_from_face(faceIdx_to_be,i)
            edges.append(newEdgeIdx)
        flatFace = flatGeom.FlatFace(verts,edges)
        return self.add_face(flatFace)
    
    def add_face_from_edge_and_new_verts(self,edge,new_verts):
        '''
        edge = FlatEdge instance
        verts => tuple or list of verts to make face
        '''
        faceIdx_to_be = len(self.flatFaces)
        edge.toFace = faceIdx_to_be
        prev_face = edge.fromFace
        edge_verts = edge.get_reversed_verts(self)
        verts = edge_verts + new_verts
        edges = []
        for i,vert in enumerate(verts):
            next_vert =  verts[ (i+1)%len(verts) ]
            if set([vert,next_vert]) != set(edge_verts):
                newEdgeIdx = self.add_edge_with_from_face(faceIdx_to_be,i)
                edges.append(newEdgeIdx)
        flatFace = flatGeom.FlatFace(verts,edges)
        return self.add_face(flatFace)

    def add_face_verts_edges(self,verts,edges):
        return self.add_face(flatGeom.FlatFace(verts,edges))

    def add_face(self,flatFace):
        self.flatFaces.append(flatFace)
        return len(self.flatFaces) - 1

############ DRAWING
    def display(self):
        #Change to show whatever aspect of island you want
        self.draw_edges()
        self.draw_verts()

    def draw_all(self):
        self.draw_faces()
        self.draw_edges()
        self.draw_verts()

    def draw_verts(self):
        for i,vert in enumerate(self.flatVerts):
            vert.display(i)

    def draw_edges(self):
        for i,edge in enumerate(self.flatEdges):
            line_guid = edge.show(self)
            edge.show_index(i,self)
            self.line_edge_map[line_guid] = edge



    def draw_faces(self, netGroupName=''):
        collection = []
        for face in self.flatFaces:
            collection.append(face.draw(self))
        #createGroup(netGroupName, collection)

############ OTHER
    def has_same_points(self,points):
        '''
        Check if the proided list of points matches the list of verts in this island. Assumes points in correct order
        '''
        for i,vert in enumerate(self.flatVerts):
            assert(vert.hasSamePoint(points[i]))

    def translate(self,vector):
        xForm = geom.Transform.Translation(vector)
        for vert in self.flatVerts:
            vert.point.Transform(xForm)

    def get_edge_instance(self,line_guid):
        # assert guid?
        return self.line_edge_map[line_guid]

    def get_edge_obj(self, edge):
        '''
        gets the object instance at the <edge> index
        '''
        return self.flatEdges[edge]

    def get_frame_reverse_edge(self,edge,face):
        assert (edge in self.flatFaces[face].edges), "edge {} does not belong to face {}".format(edge,face)
        flatEdge = self.flatEdges[edge]
        edgeVec = flatEdge.get_edge_vec(self)
        edgeVec.Reverse()
        pntA,pntB = flatEdge.get_coordinates(self)
        normal = self.flatFaces[face].get_normal()
        return trans.Frame.create_frame_from_normal_and_x(pntB,normal,edgeVec)
