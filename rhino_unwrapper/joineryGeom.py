import rhinoscriptsyntax as rs
import edgeGeom
reload(edgeGeom)

#TODO:
''' 
deal with tabs to close to endpoints:
    solA: paddin on both sides of edge
      use: rs.CurveParameter
    solB: center geom on edge
    solC:

twisted tab bug >  DONE involved assumption about side of geom being drawn
small edges bug > DONE

'''

class RivetSystem(object):

    def __init__(self,hole_offset,rivet_diameter,spacing,tab_padding):
        self.hole_offset = hole_offset
        self.rivet_diameter = rivet_diameter
        self.spacing = spacing
        self.tab_padding = tab_padding
        self.geom_temp = []
        self.temp_geom = []
        self.normal = (0,0,1)

    def _get_base_points(self,curve_id):
        first_point = rs.CurveStartPoint(curve_id)
        last_point = rs.CurveEndPoint(curve_id)
        base_points = rs.DivideCurveLength(curve_id,self.spacing, create_points=False, return_points=True)
        base_points = base_points[1:]
        return first_point,base_points,last_point

    def _get_length_threshold(self):
        return self.spacing+self.rivet_diameter+2.0*self.tab_padding

    def _is_small_edge(self,curve_id):
        threshold = self._get_length_threshold()
        if rs.CurveLength(curve_id) <= threshold:
            return True
        return False

    def _offset_positions(self,curve_id,left_side,mid_geom_func,end_geom_func=None):
        '''

           |  |  |  |  |  |  |  |
        I------------------------->J

        '''
        first_point,base_points,last_point = self._get_base_points(curve_id)
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

    def inner_joinery(self,curve_id,left_side):

        def geomFunction(pntI,pntJ,prev_point):
            circle = rs.AddCircle(rs.PlaneFromNormal(pntI,self.normal),self.rivet_diameter/2.0)
            self.geom_temp.append(circle)
            return None,None

        if self._is_small_edge(curve_id):
            return None
        return self._offset_positions(curve_id,left_side,geomFunction)

    def outer_joinery(self,curve_id,left_side):
        
        def rivet_tab(pntI,pntJ,prev_point):
            radius = self.rivet_diameter/2.0+self.tab_padding
            a,b,c,d,e = edgeGeom.get_arc_rod_points(pntI,pntJ,radius,not left_side)
            arc = rs.AddArc3Pt(b,d,c)
            line_ab = rs.AddLine(a,b)
            line_de = rs.AddLine(d,e)
            hole = rs.AddCircle(rs.PlaneFromNormal(pntI,self.normal),self.rivet_diameter/2.0)   
            line_connect = rs.AddLine(prev_point,a)
            self.geom_temp.extend([line_connect,line_ab,arc,line_de,hole])
            return a,e
        def end_geom(end_point,last_point):
            self.geom_temp.append(rs.AddLine(end_point,last_point))
        
        if self._is_small_edge(curve_id):
            return None
        return self._offset_positions(curve_id,left_side,rivet_tab,end_geom)



