import unittest
import rhinoscriptsyntax as rs
import joinery
reload(joinery)

class RivetPositionsTestCase(unittest.TestCase):
    def setUp(self):
        self.curve_id = rs.AddLine([0,0,0],[5,5,0])
        self.offset = 2.0
        self.length= 2.0

    def test_rivet_positions(self):
        joinery.rivet_positions(self.curve_id,self.offset,self.length)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(RivetPositionsTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
