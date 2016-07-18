import unittest
import rhinoscriptsyntax as rs
import island
reload(island)

ANGLE = 1

class StubbedMesh(object):
    def getEdgeAngle(self,edge):
        return ANGLE

class FoldEdgeTestCase(unittest.TestCase):
    def setUp(self):
        self.island = island.make_triangulated_square_island()
        self.fold_edge = self.island.flatEdges[2]

    def test_show_crease(self):
        #self.island.draw_edges()
        self.fold_edge._show_crease(self.island)
    
    def test_sends_getEdgeAngle(self):
        #NOTE: this would probably be a place to do a mock object
        self.fold_edge.meshEdgeIdx = 1
        angle = self.fold_edge.get_angle_in_mesh(StubbedMesh())
        self.assertEqual(angle,ANGLE)

if __name__=="__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(FoldEdgeTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
