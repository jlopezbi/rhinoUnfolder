import rhinoscriptsyntax as rs
import edgeGeom
reload(edgeGeom)

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
    pntA,pntC,pntB = edgeGeom.get_arc_cap(pntI,pntJ,offset,radius)
    pntD,pntF,pntE = edgeGeom.get_arc_cap(pntJ,pntI,offset,radius)
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

