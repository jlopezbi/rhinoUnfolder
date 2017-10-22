import rhinoscriptsyntax as rs

#seems like should be a class, but a class just to run a bunch of related functions? Seems silly. 
#In this case the inputs are relatively simple, but there can be
#many operations on them!
#this seems like a case for functional programming, although I 
#don't really know what that means..

'''
Observation: all of these pill shaped geoms involve at their core
generating points. The points at there core involve findinging offset vectors and adding them to the base points I,J
True for stuff in creaseGeom and joineryGeom. Think on that one!

'''
class LineChunker(object):
    #NOTE: not curretnly functional; still an idea
    '''
        |--|-|--|-|--|-|
    I ---------------------> J
    chunk up into rectangular cells which gets geometry applied to them, 
    sort of like paneling tools!
    could even apply a predefined set of curves that sit inside a bounding box that is the same size..
    or like the bounding box of those curves is what determines that parameters for the chunker
    '''

    def __init__(self,padding,spacing,chunk_width,chunk_length):
        self.padding = padding
        self.spacing = spacing
        self.chunk_width = chunk_width
        self.chunk_length = chunk_length

    def _get_padded_line(self,line_id):
        a = rs.CurveArcLengthPoint(line_id,self.padding,from_start=True)
        b = rs.CurveArcLengthPoint(line_id,self.padding,from_start=False)
        temporary_line = rs.AddLine(a,b)
        return temporary_line

    def chunk_up_line(self,line_id):
        pass

class CombOnLineCreator(object):
    '''
       | | | | |
    I ----------- J
    '''

    def __init__(self,offset,spacing,edge_padding):
        self.offset = offset
        self.spacing = spacing
        self.edge_padding = edge_padding
        self.geom_temp = []
        self.temp_geom = []
        self.normal = (0,0,1)

    def _left_over_space(self,curve_id):
        '''
        compute the remaning space that will result
        from segmenting the given curve with self.spacing chunks.
        '''
        length = rs.CurveLength(curve_id)
        extra = length - int(length/self.spacing)*self.spacing
        return extra
    
    def _get_centering_vec(self,curve_id,extra_space):
        '''
        gets the vector that is aligned with curve, and whos length
        is half of extra_space
        '''
        dist = extra_space/2.0
        start = rs.CurveStartPoint(curve_id)
        end = rs.CurveEndPoint(curve_id)
        vec = rs.VectorSubtract(end,start)
        vec_unit = rs.VectorUnitize(vec)
        vec_scaled = rs.VectorScale(vec_unit,dist)
        return vec_scaled

    def _get_base_points(self,curve_id):
        base_points = rs.DivideCurveLength(curve_id,self.spacing, create_points=False, return_points=True)
        return base_points
    
    def _shift_points(self,points,vec):
        x_form = rs.XformTranslation(vec)
        return rs.PointArrayTransform(points,x_form)

    def _get_length_threshold(self):
        return self.spacing

    def _is_small_edge(self,curve_id):
        threshold = self._get_length_threshold()
        if rs.CurveLength(curve_id) <= threshold:
            return True
        return False

    def _get_padded_line(self,line_id):
        a = rs.CurveArcLengthPoint(line_id,self.edge_padding,from_start=True)
        b = rs.CurveArcLengthPoint(line_id,self.edge_padding,from_start=False)
        if not a or not b:
            return None
        temporary_line = rs.AddLine(a,b)
        return temporary_line

    def get_comb_points(self,curve_id,left_side):
        '''

           |  |  |  |  |  |  |  |
        I------------------------->J
        'comb' is centered on line.
        returns ordered base points and offset points
        to form a 'comb'

        '''
        first_point,last_point = get_first_and_last_points(curve_id)
        if self._is_small_edge(curve_id):
            return None
        small_line = self._get_padded_line(curve_id)
        if self._is_small_edge(small_line):
            return None
        base_points = self._get_base_points(small_line)
        extra_space = self._left_over_space(small_line)
        shift_vec = self._get_centering_vec(small_line,extra_space)
        rs.DeleteObject(small_line)
        base_points = self._shift_points(base_points,shift_vec)
        vec_perp_offset = get_sized_perpendicular_vector(first_point,
                                                                  last_point,
                                                                  self.offset,
                                                                  left_side)
        temp_points = list(base_points) 
        offset_points = self._shift_points(temp_points,vec_perp_offset)
        return zip(base_points,offset_points)




#END CLASS
def get_first_and_last_points(curve_id):
    first_point = rs.CurveStartPoint(curve_id)
    last_point = rs.CurveEndPoint(curve_id)
    return first_point,last_point


def get_arc_rod_points(pntI,pntJ,radius,reverse):
    '''
         D ------------------E
       /
      C--I------------------>J
       \ 
         B ------------------A
    reverse will reverse order of points depicted above
    '''
    offset = -1.0*radius
    pntB,pntC,pntD = get_arc_cap(pntI,pntJ,offset,radius)
    vec_A = get_sized_perpendicular_vector(pntI,pntJ,radius,left=False)
    pntA = rs.VectorAdd(pntJ,vec_A)
    vec_E = get_sized_perpendicular_vector(pntI,pntJ,radius,left=True)
    pntE = rs.VectorAdd(pntJ,vec_E)
    pnts =  [pntA,pntB,pntC,pntD,pntE]
    if reverse: pnts.reverse()
    return pnts

def fuse_curves(curves):
    #TODO: move to rhino helpers?
    if not curves:
        return
    curves = rs.JoinCurves(curves,delete_input=True)
    assert len(curves) == 1, "in fuse_curves() JoinCurves failed"
    curve = curves[0]
    return curve

def get_sized_perpendicular_vector(pntI,pntJ,size,left=True):
    vec_perp = get_perpendicular_vector_to_points(pntI,pntJ,left)
    return rs.VectorScale(vec_perp,size)

def get_perpendicular_vector_to_points(pntI,pntJ,left=True):
    '''
    returns a unitized vector perpendicular to the vector formed 
    from pntI to pntJ
    ^
    |
    I-------> J
    '''
    normal = [0,0,1]
    angle = 90.0
    if not left:
        angle = -1.0 * angle
    vec = rs.VectorSubtract(pntJ,pntI)
    vec = rs.VectorRotate(vec,angle,normal)
    return rs.VectorUnitize(vec)

def get_arc_cap(pntI,pntJ,offset,radius):
    '''
    finds three points, A,B,C making up a half-circle arc. returns in order [A,C,B]
    oriented on the vector. Assumes vector lies in XY plane
             C
           /
     I--- B ------------------->J
           \ 
             A
    '''
    normal = [0,0,1]
    vec = rs.VectorSubtract(pntJ,pntI)
    vecB_unit = rs.VectorUnitize(vec)
    vecB_sized = rs.VectorScale(vecB_unit,offset)
    pointB = rs.VectorAdd(pntI,vecB_sized)
    vec_base = rs.VectorScale(vecB_unit,offset+radius)
    vec_perp_c = get_sized_perpendicular_vector(pntI,pntJ,radius,True)
    vec_C = rs.VectorAdd(vec_base,vec_perp_c)
    pointC = rs.VectorAdd(pntI,vec_C)
    vec_perp_a = rs.VectorReverse(vec_perp_c)
    vec_A = rs.VectorAdd(vec_base,vec_perp_a)
    pointA = rs.VectorAdd(pntI,vec_A)
    return pointA, pointB, pointC

