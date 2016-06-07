import rhinoscriptsyntax as rs
import rhino_helpers
reload(rhino_helpers)

def slot_crease(pntA,pntB):
    offset = .125
    width = .025
    vecA = rhino_helpers.getVectorForPoints(pntA,pntB)
    vecA_unit = rs.VectorUnitize(vecA)
    vecA_sized = rs.VectorScale(vecA_unit,offset)

    vecB_sized = rs.VectorReverse(vecA_sized)
    posA = rs.VectorAdd(pntA,vecA_sized)
    posB = rs.VectorAdd(pntB,vecB_sized)
    cA = rs.AddCircle(posA,width)
    cB = rs.AddCircle(posB,width)
    rs.AddObjectsToGroup([cA,cB],self.group_name)

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
