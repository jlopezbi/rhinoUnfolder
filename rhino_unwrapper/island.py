import flatGeom
import flatEdge
import rhino_helpers 
import transformations as trans
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs
reload(flatGeom)
reload(flatEdge)
reload(rhino_helpers)
reload(trans)


island_plane = rs.WorldXYPlane()

def make_triangulated_square_island(island=None):
    '''
    This function gives a demo of how layout makes an
    island. This is also usefull for testing stuff on
    island and its elements
    '''
    if not island: island=Island()
    #First Face
    pnt0 = geom.Point3d(0.0,0.0,0.0) #0
    pnt1 = geom.Point3d(5.0,0.0,0.0) #1
    pnt2 = geom.Point3d(0.0,5.0,0.0)
    pnt3 = geom.Point3d(5.0,5.0,0.0)
    island.add_dummy_elements()
    island.add_vert_from_point(pnt0)
    island.add_vert_from_point(pnt1)
    island.change_to_naked_edge(edge=0)
    island.layout_add_vert_point(pnt2)
    edge = island.layout_add_edge(index=1)
    island.change_to_cut_edge(edge)
    fold_edge = island.layout_add_edge(index=2)
    island.change_to_fold_edge(fold_edge)
    island.layout_add_face(baseEdge=0)

    #Second face
    island.layout_add_vert_point(pnt3)
    edge = island.layout_add_edge(index=1)
    island.change_to_cut_edge(edge)
    edge = island.layout_add_edge(index=2)
    island.change_to_cut_edge(edge)
    island.layout_add_face(baseEdge=fold_edge)
    return island

def make_five_by_five_square_island(island=None):
    if not island: island=Island()
    island.add_vert_from_points(0.0,0.0,0.0) #0
    island.add_vert_from_points(5.0,0.0,0.0) #1
    island.add_vert_from_points(0.0,5.0,0.0) #2
    island.add_vert_from_points(5.0,5.0,0.0) #3
    face = island.add_first_face_from_verts(0,1,3,2)
    for edge in range(len(island.flatEdges)): island.change_to_cut_edge(edge)
    return island

class Island(object):

    def __init__(self):
        '''
        stores flatVerts,flatEdges and flatFaces and draws itself
        Random thought: each island could have a map 
        Yooo could have a class for each collection like planton..
        '''
        #TODO: consider clearing out unused functionality
        self.flatVerts = []
        self.flatEdges = []
        self.flatFaces = []  
        # quick fix for finding only cut edges.
        # some day find a better way, perhaps have three arrays, or maybe put cut edges first..
        self.cut_edge_lines= []
        self.groupToEdge_map= {}
        self.temp_edges = []
        self.temp_verts = []
        self.debug_visualize = False
        self.group_name = rs.AddGroup()

################## LAYOUT
    def add_dummy_elements(self): 
        '''
        to be used for layout; initializes with edge and face
        '''
        self.dummyFace = self.add_face(flatGeom.FlatFace([0,1],[0]))
        self.dummyEdge = self.add_edge_with_from_face(face=0,index=0)

    def change_to_fold_edge(self,edge):
        baseEdge = self.flatEdges[edge]
        self.flatEdges[edge] = flatEdge.create_fold_edge_from_base(baseEdge)

    def change_to_cut_edge(self,edge):
        baseEdge = self.flatEdges[edge]
        self.flatEdges[edge] = flatEdge.create_cut_edge_from_base(baseEdge)

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
    def layout_add_edge(self,index=None,meshEdge=None,edgeAngle=None):
        '''
        designed for layout: edge gets added before face gets added
        '''
        newFaceIdx = len(self.flatFaces)
        newEdge = self.add_edge(flatEdge.FlatEdge(fromFace=newFaceIdx,indexInFace=index,meshEdgeIdx=meshEdge,angle=edgeAngle))
        self.temp_edges.append(newEdge)
        return newEdge

    def update_edge_to_face(self,edge,toFace):
        edge_obj = self.get_edge_obj(edge)
        edge_obj.toFace = toFace

    def add_edge_with_from_face(self,face=None,index=None):
        edgeIdx =  self.add_edge(flatEdge.FlatEdge(face,index))
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
    def clear(self):
        ''' clears all geometry for island'''
        objects = rs.ObjectsByGroup(self.group_name)
        rs.DeleteObjects(objects)
        self.groupToEdge_map= {}
        self.cut_edge_lines= []

    #show, display, draw, render, ?
    def display(self):
        #Change to show whatever aspect of island you want
        self.draw_edges()
        #self.draw_verts()
    
    def get_perimeter_geometry(self):
        return self.cut_edge_lines

    def draw_all(self):
        self.draw_faces()
        self.draw_edges()
        self.draw_verts()

    def draw_verts(self):
        for i,vert in enumerate(self.flatVerts):
            vert.display(self.group_name)
    
    def show_vert_indices(self):
        for i, vert in enumerate(self.flatVerts):
            vert.display_index(i,self.group_name)

    def draw_edges(self):
        for i,edge in enumerate(self.flatEdges):
            #NOTE: when a cutEdge shows, it adds its line_guid to island.cut_edge_lines
            edge.show(self)
            #edge.show_index(i,self)
            self.groupToEdge_map[edge.group_name] = i

    def draw_faces(self):
        for face in self.flatFaces:
            face.draw(self)

############ OTHER
    def has_same_points(self,points):
        '''
        Check if the proided list of points matches the list of verts in this island. Assumes points in correct order
        '''
        for i,vert in enumerate(self.flatVerts):
            assert(vert.hasSamePoint(points[i])), "For vert index {}, the actual position is {}, while the supplied point is {}".format(i,vert.point,points[i])

    def translate(self,vector):
        xForm = geom.Transform.Translation(vector)
        for vert in self.flatVerts:
            vert.point.Transform(xForm)

    def get_index_for_group(self,group):
        return self.groupToEdge_map[group]

    def get_edgeInstance_for_guid(self,line_guid):
        # assert guid?
        index = get_index_for_guid(line_guid)
        return self.flatEdges[index]

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

############ AVOIDING OTHER ISLANDS
    
    def get_boundary_polyline(self):
        '''
        NOTE: draw_edges must be called before running this function!
        find the polyline composed of all cut edges, which by definition form the 
        boundary of this island
        '''
        assert self.cut_edge_lines, "cut_edge_linesis empty, make sure have drawn island first"
        new_curves = rs.JoinCurves(self.cut_edge_lines,delete_input=False)
        assert len(new_curves)==1, "more than one curve created!"
        curve = new_curves[0]
        assert rs.IsCurveClosed(curve), "curve {} is not closed".format(curve)
        return curve

    def get_bounding_rectangle(self):
        '''
        Assuming the island is planar, gets the four points bounding the current representation
        of the island. BoundingBox returns a list of 8 points. This returns the first four (the
        base of the box)
        '''
        full_box = rs.BoundingBox(self.get_perimeter_geometry(),view_or_plane=island_plane)
        return full_box[0:4]
    
    def is_overlapping(self,other_island):
        this_perimeter = self.get_boundary_polyline()
        other_perimeter = other_island.get_boundary_polyline()
        assert rs.IsCurvePlanar(this_perimeter), "curve of this island not planar"
        assert rs.IsCurvePlanar(other_perimeter), "curve of other island not planar"
        assert rs.IsCurveInPlane(this_perimeter,island_plane), "this island not in {} plane".format(island_plane)
        assert rs.IsCurveInPlane(other_perimeter,island_plane), "input island not in {} plane".format(island_plane)
        relation = rs.PlanarClosedCurveContainment(this_perimeter,other_perimeter)
        rs.DeleteObjects([this_perimeter,other_perimeter])
        assert relation!=None, "PlanarClosedCurveContainment failed"
        if relation!=0:
            return True
        else:
            return False

    def move_to_edge(self,other_island,padding=1.0):
        this_bouding_rect = self.get_bounding_rectangle()
        other_boundary_rect = other_island.get_bounding_rectangle()
        this_x_lower = this_bouding_rect[0].X
        other_x_upper = other_boundary_rect[1].X
        horizontal_move_vec = geom.Vector3d(padding+other_x_upper-this_x_lower,0,0)
        self.clear()
        self.translate(horizontal_move_vec)
        self.draw_edges()
        
    def avoid_other(self,other_island,padding=1.0):
        '''
        if this island overlaps other_island, translate this island
        horizontally to the right so that its bounding rectangle clears 
        that of other_island
        '''
        if self.is_overlapping(other_island):
            self.move_to_edge(other_island,padding)




