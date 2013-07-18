import Rhino
import System.Drawing.Color
 
line_color = System.Drawing.Color.FromArgb(0,255,0)
 
def DynamicDrawFunc( sender, args ):
    point = args.CurrentPoint
    args.Display.DrawLine( point, Rhino.Geometry.Point3d(point.X, point.Y, point.Z+10), line_color, 1)
   
gp = Rhino.Input.Custom.GetPoint()
gp.DynamicDraw += DynamicDrawFunc
gp.Get()