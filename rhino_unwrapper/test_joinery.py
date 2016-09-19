import unittest
import rhinoscriptsyntax as rs
import joineryGeom
reload(joineryGeom)

class RivetSystemTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        offset = 1.0
        spacing = 1.0
        rivet_diameter = .3
        tab_padding = .16
        edge_padding = 1.0
        cls.joinery = joineryGeom.RivetSystem(offset,rivet_diameter,spacing,tab_padding,edge_padding)

    def setUp(self):
        self.curve_id = rs.AddLine([0,0,0],[5,7,0])

    def tearDown(self):
        rs.DeleteObjects(self.curve_id)

    def test_small_outer_joinery(self):
        line = rs.AddLine((0,0,0),(.1,0,0))
        self.assertEqual(None,self.joinery.outer_joinery(line,True))

    def test_small_inner_joinery(self):
        line = rs.AddLine((0,0,0),(.1,0,0))
        self.assertEqual(None,self.joinery.inner_joinery(line,True))
    

    def test_rivet_tabs(self):
        self.joinery.outer_joinery(self.curve_id,True)
        self.joinery.outer_joinery(self.curve_id,False)

    def test_rivet_holes(self):
        self.joinery.inner_joinery(self.curve_id,False)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(RivetSystemTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
