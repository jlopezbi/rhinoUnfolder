import rhinoscriptsyntax as rs

objs = rs.GetObjects("Select curves to join", rs.filter.curve)

if objs: 
    new_curves = rs.JoinCurves(objs,delete_input=True)

print new_curves
print "there are {} curves".format(len(new_curves))


