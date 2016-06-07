import unittest
import rhinoscriptsyntax as rs
import creaseGeom
reload(creaseGeom)

class SlotCreaseTestCase(unittest.TestCase):

    def test_slot_crease(self):
        edge_length = 10.0
        pntI = (0.0,0.0,0.0)
        pntJ = (edge_length,0.0,0.0)
        offset = 2.0
        width = 1.0
        creaseGeom.slot_crease(pntI,pntJ,offset,width)

    def test_get_arc_cap_works(self):
        offset = 2
        radius = 1
        pntA,pntC,pntB = creaseGeom.get_arc_cap((0.0,0.0,0.0,), (5.0,0.0,0.0),offset,radius)
        self.assertTrue(rs.PointCompare(pntB,(offset,0.0,0.0)) )
        self.assertTrue(rs.PointCompare(pntA,(offset+radius,-radius,0.0)) )
        self.assertTrue(rs.PointCompare(pntC,(offset+radius,radius,0.0)) )
        rs.AddArc3Pt(pntA,pntC,pntB)
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(SlotCreaseTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

