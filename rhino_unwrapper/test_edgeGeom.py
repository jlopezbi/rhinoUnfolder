import unittest
import rhinoscriptsyntax as rs
import edgeGeom
reload(edgeGeom)

class edgeGeomTestCase(unittest.TestCase):
    def setUp(self):
        self.pntI = (0,0,0)
        self.pntJ = (10,5,0)
        self.radius = 2.5
        self.color = (0,255,0)
        rs.AddLine(self.pntI,self.pntJ)

    def test_create_arc_rod(self):
        a,b,c,d,e = edgeGeom.get_arc_rod_points(self.pntI,self.pntJ,self.radius,self.color)

    def test_get_arc_cap_works(self):
        offset = 2
        radius = 1
        pntA,pntB,pntC = edgeGeom.get_arc_cap((0.0,0.0,0.0,), (5.0,0.0,0.0),offset,radius)
        self.assertTrue(rs.PointCompare(pntB,(offset,0.0,0.0)) )
        self.assertTrue(rs.PointCompare(pntA,(offset+radius,-radius,0.0)) )
        self.assertTrue(rs.PointCompare(pntC,(offset+radius,radius,0.0)) )
        rs.AddArc3Pt(pntA,pntC,pntB)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(edgeGeomTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

