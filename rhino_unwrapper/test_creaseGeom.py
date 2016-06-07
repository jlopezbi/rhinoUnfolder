import unittest
import rhinoscriptsyntax as rs
import creaseGeom
reload(creaseGeom)

class SlotCreaseTestCase(unittest.TestCase):

    def test_get_arc_cap_works(self):
        pntA,pntB,pntC = creaseGeom.get_arc_cap((0.0,0.0,0.0,), (5.0,0.0,0.0),2,1)
        #TODO: add assertions for point locations
        rs.AddArc3Pt(pntA,pntB,pntC)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(SlotCreaseTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

