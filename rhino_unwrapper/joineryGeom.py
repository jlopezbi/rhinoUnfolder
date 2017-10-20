import rhinoscriptsyntax as rs
import edgeGeom
reload(edgeGeom)

#NOTE: currently working here!
''' 
Errors out now for small edges, probably has to do with getting small_line. :(
notion: this really can be split up more:
1: chunking up a line into segments < seperate module
2: applying geometry to all the segments < maybe connected module
3: processing that geometry (i.e. joining it if necessary)

the geometry creation would be its own module
like: rivet_tabs, slots, user_defined,  etc.

deal with tabs to close to endpoints:
    solA: paddin on both sides of edge
      use: rs.CurveParameter
    solB: center geom on edge
    solC:

twisted tab bug >  DONE involved assumption about side of geom being drawn
small edges bug > DONE

'''

class NullSystem(object):

    def __init__(self):
        '''
        does not create any joinery geometry
        '''
        pass

    def inner_joinery(self, curve_id, left_side):
        return None

    def outer_joinery(self, curve_id, left_side):
        return None

class RivetSystem(object):

    def __init__(self,hole_offset,rivet_diameter,spacing,tab_padding,edge_padding):
        self.hole_offset = hole_offset
        self.rivet_diameter = rivet_diameter
        self.spacing = spacing
        self.tab_padding = tab_padding
        self.edge_padding = edge_padding
        self.geom_temp = []
        self.normal = (0,0,1)
        self.comb_creator = edgeGeom.CombOnLineCreator(self.hole_offset,self.spacing,self.edge_padding)

    def _clear_geom(self):
        self.geom_temp = []

    def rivet_hole(self,pntI):
        circle = rs.AddCircle(rs.PlaneFromNormal(pntI,self.normal),self.rivet_diameter/2.0)
        self.geom_temp.append(circle)

    def rivet_tab(self,pntJ,pntI,prev_point,left_side):
        radius = self.rivet_diameter/2.0+self.tab_padding
        a,b,c,d,e = edgeGeom.get_arc_rod_points(pntI,pntJ,radius,not left_side)
        arc = rs.AddArc3Pt(b,d,c)
        line_ab = rs.AddLine(a,b)
        line_de = rs.AddLine(d,e)
        hole = rs.AddCircle(rs.PlaneFromNormal(pntI,self.normal),self.rivet_diameter/2.0)   
        line_connect = rs.AddLine(prev_point,a)
        self.geom_temp.extend([line_connect,line_ab,arc,line_de,hole])
        return a,e

    def inner_joinery(self,curve_id,left_side):
        self._clear_geom()
        comb_points = self.comb_creator.get_comb_points(curve_id,left_side)
        if not comb_points:
            return None
        for (not_used,point) in comb_points:
            self.rivet_hole(point)
        return self.geom_temp

    def end_geom(end_point,last_point):
        self.geom_temp.append(rs.AddLine(end_point,last_point))

    def outer_joinery(self,curve_id,left_side):
        self._clear_geom()
        comb_points = self.comb_creator.get_comb_points(curve_id,left_side)
        if not comb_points:
            return None
        start,end = edgeGeom.get_first_and_last_points(curve_id) 
        prev_point = start
        for (base_point,offset_point) in comb_points:
            s,e = self.rivet_tab(base_point,offset_point,prev_point,left_side)
            prev_point = e
        self.geom_temp.append(rs.AddLine(e,end))
        if len(self.geom_temp)>=2:
            return rs.JoinCurves(self.geom_temp,delete_input=True)
        else:
            return self.geom_temp 

class TabSystem(object):

    def __init__(self):
        pass

    def inner_joinery(self, curve_id, left_side):
        return None

    def outer_joinery(self, curve_id, left_side):
        return None



'''
#Depricated function that used functional approahc
def _offset_positions(self,curve_id,left_side,mid_geom_func,end_geom_func=None):

           |  |  |  |  |  |  |  |
        I------------------------->J

        first_point = rs.CurveStartPoint(curve_id)
        last_point = rs.CurveEndPoint(curve_id)
        small_line = self._get_padded_line(curve_id)
        if self._is_small_edge(small_line):
            return None
        base_points = self._get_grid_points(small_line)
        rs.DeleteObject(small_line)
        vec_perp_offset = edgeGeom.get_sized_perpendicular_vector(first_point,
                                                                  last_point,
                                                                  self.hole_offset,
                                                                  left_side)
        hole_points = []
        prev_point = first_point
        if end_geom_func == None:
            end_geom_func = lambda x,y: None
        for i,base_point in enumerate(base_points):
            new_point = rs.VectorAdd(base_point ,vec_perp_offset)
            hole_points.append(new_point)
            start_point,end_point = mid_geom_func(new_point,base_point,prev_point)
            prev_point = end_point
        end_geom_func(end_point,last_point)
        curves_to_join = self.geom_temp
        self.geom_temp = []
        if len(curves_to_join)>=2:
            return rs.JoinCurves(curves_to_join,delete_input=True)
        else:
            return curves_to_join
'''

