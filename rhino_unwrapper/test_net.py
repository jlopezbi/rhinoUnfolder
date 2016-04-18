import unittest
import Net

reload(Net)

class IslandTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.island = Net.Island()

    def test_add_vert(self):
        self.island.add_vert_from_points(0.0,0.0,0.0)
        self.island.add_vert_from_points(5.0,0.0,0.0)
        self.island.add_vert_from_points(0.0,5.0,0.0)
        self.island.add_vert_from_points(5.0,5.0,0.0)
        self.island.add_edge_from_verts(0,1)
        
        self.island.draw_verts()
        self.island.draw_faces()
        self.island.draw_edges()

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(IslandTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
