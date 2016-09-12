import rhinoscriptsyntax as rs


def inner_rivet_holes(curve_id,offset,spacing,left_side):
    #hole_points = rivet_positions(curve_id,offset,spacing,  
    pass


def rivet_positions(curve_id,offset,spacing,left_side=True):
    '''

       |  |  |  |  |  |  |  |
    I------------------------->J

    '''
    normal = [0,0,1]
    base_points = rs.DivideCurveLength(curve_id,spacing, create_points=False, return_points=True)
    base_points = base_points[1:] 
    base_vec = rs.CurveTangent(curve_id,0.0)
    vec_perp = rs.VectorRotate(base_vec,90.0,normal)
    vec_perp_unit = rs.VectorUnitize(vec_perp)
    vec_perp_offset = rs.VectorScale(vec_perp_unit,offset)
    hole_points = []
    for point in base_points:
        new_point = rs.VectorAdd(point,vec_perp_offset)
        hole_points.append(new_point)
    return hole_points



class Tab(object):

    def __init__(self):
        self.tab_width = tab_width

class RivetSystem(object):
    def __init__(self,hole_offset,rivet_diameter,spacing):
        self.hole_offset = hole_offset
        self.rivet_diameter = rivet_diameter

    def create_holes(self):
        pass

    def create_tabs(self):
        pass


