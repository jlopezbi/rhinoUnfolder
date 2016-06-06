import unittest
import rhinoscriptsyntax as rs
import island
reload(island)

class FoldEdgeTestCase(unittest.TestCase):
    def setUp(self):
        self.island = island.make_triangulated_square_island()
        self.island.draw_edges()
        self.fold_edge = self.island.flatEdges[2]

    def test_show_crease(self):
        pass
        #self.fold_edge._show_crease(self.island)

if __name__=="__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(FoldEdgeTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
