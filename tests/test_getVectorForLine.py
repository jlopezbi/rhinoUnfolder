#test get vec from line
from layout import *
import rhinoscriptsyntax as rs
import Rhino

curve = rs.GetObject("select Line")
if curve:
  endPnt = rs.CurveEndPoint(curve) #these are point3d
  startPnt = rs.CurveStartPoint(curve)

  fEdge = FlatEdge(0,[endPnt,startPnt])
  fEdge.geom = Rhino.Geometry.Line(startPnt,endPnt)
  vec = fEdge.getVectorFromLine()

  rs.AddPoint(vec)