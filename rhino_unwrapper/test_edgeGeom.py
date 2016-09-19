import unittest
import rhinoscriptsyntax as rs
import edgeGeom
reload(edgeGeom)

class CombOnLineTestCase(unittest.TestCase): 
    def setUp(self):
        self.pntI = (0,0,0)
        self.pntJ = (-10,0,0)
        self.line = rs.AddLine(self.pntI,self.pntJ)
        offset = 1
        spacing = 2.85
        edge_padding = 2.5
        self.comb_creator = edgeGeom.CombOnLineCreator(offset,spacing,edge_padding)

    def test_finds_extra(self):
        extra = self.comb_creator._left_over_space(self.line)
        correct = 1.450
        self.assertAlmostEqual(extra,correct,places=8)

    def test_gets_correct_centering_vector(self):
        extra = self.comb_creator._left_over_space(self.line)
        vec = self.comb_creator._get_centering_vec(self.line,extra)
        self.assertAlmostEqual(vec[0],-extra/2.0)

    def test_small_edges(self):
        length_thresh = self.comb_creator._get_length_threshold()
        short_curve = rs.AddLine([0,0,0],[length_thresh,0,0])
        self.assertEqual((None,None),self.comb_creator.outer_joinery(short_curve,True))

    def test_makes_points(self):
        base,offset = self.comb_creator.get_comb_points(self.line,False)
        for pnt in base: rs.AddPoint(pnt)
        for pnt in offset: rs.AddPoint(pnt)

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
    suite.addTest(loader.loadTestsFromTestCase(CombOnLineTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)


