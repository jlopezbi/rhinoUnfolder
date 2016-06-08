import rhinoscriptsyntax as rs
import rhino_helpers
reload(rhino_helpers)

def pill_shape(pntI,pntJ,offset,width,color=(0,0,0)):
    '''
    creates a pill shape between the two points
    returns the polycurve guid
            C ---  D
           /        \
    I --- B -------- E ----> J
           \        /
             A -- F
    '''
    radius = width/2.0
    pntA,pntC,pntB = get_arc_cap(pntI,pntJ,offset,radius)
    pntD,pntF,pntE = get_arc_cap(pntJ,pntI,offset,radius)
    first_arc = rs.AddArc3Pt(pntA,pntC,pntB)
    second_arc = rs.AddArc3Pt(pntD,pntF,pntE)    
    first_line = rs.AddLine(pntC,pntD)
    second_line = rs.AddLine(pntF,pntA)
    geom = [first_arc,second_arc,first_line,second_line]    
    curves = rs.JoinCurves(geom,delete_input=True)
    assert len(curves) == 1, "in pill_shape JoinCurves failed"
    curve = curves[0]
    rs.ObjectColor(curve,color)
    return curve

def get_arc_cap(pntI,pntJ,offset,radius):
    '''
    finds three points, A,B,C making up a half-circle arc. returns in order [A,C,B]
    ortiented on the vector. Assumes vector lies in XY plane
             C
           /
     I--- B ------------------->J
           \ 
             A
    '''
    normal = [0,0,1]
    #vec = rhino_helpers.getVectorForPoints(pntI,pntJ)
    vec = rs.VectorSubtract(pntJ,pntI)
    vecB_unit = rs.VectorUnitize(vec)
    vecB_sized = rs.VectorScale(vecB_unit,offset)
    pointB = rs.VectorAdd(pntI,vecB_sized)
    vec_base = rs.VectorScale(vecB_unit,offset+radius)
    vec_perp = rs.VectorRotate(vec,90.0,normal)
    vec_perp_unit = rs.VectorUnitize(vec_perp)
    vec_perp_c = rs.VectorScale(vec_perp_unit,radius)
    vec_C = rs.VectorAdd(vec_base,vec_perp_c)
    pointC = rs.VectorAdd(pntI,vec_C)
    vec_perp_a = rs.VectorReverse(vec_perp_c)
    vec_A = rs.VectorAdd(vec_base,vec_perp_a)
    pointA = rs.VectorAdd(pntI,vec_A)
    return pointA, pointC, pointB
