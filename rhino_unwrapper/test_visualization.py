import unittest
import visualization as vis
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs
reload(vis)

def setUpModule():
    print("****Visualization Test Module set-up")

def tearDownModule():
    print("****MODULE TORN DOWN")
    rs.DeleteObjects(rs.AllObjects())
class VisualizationTestCase(unittest.TestCase):

    def test_rhino_line(self):
        pntA = geom.Point3d(0,0,0)
        pntB = geom.Point3d(2,2,0)
        line = vis.rhino_line(pntA,pntB)
        return line
    
    def test_show_line(self):
        line = self.test_rhino_line()
        vis.show_line(line,(0,255,0,0))

    def test_draw_arrow(self):
        line = self.test_rhino_line()
        vis.draw_arrow(line,(0,255,0,255))

    def test_drawVector(self):
        pos = geom.Point3d(0,0,0)
        vec = geom.Vector3d(2,-2,0)
        vis.drawVector(vec,pos)

if __name__ == "__main__":
    suiteB = unittest.TestLoader().loadTestsFromTestCase(VisualizationTestCase)
    unittest.TextTestRunner(verbosity=2).run(suiteB)
