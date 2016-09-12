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
