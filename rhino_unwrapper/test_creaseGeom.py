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
        color = (255,0,255)
        creaseGeom.pill_shape(pntI,pntJ,offset,width,color)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(SlotCreaseTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

