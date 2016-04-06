import unittest
import mesh
reload(mesh)

class MeshTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mesh = mesh.make_test_mesh()

    def test_get_set_of_edges(self):
        self.assertEqual(self.mesh.get_set_of_edges(),set(range(16)))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(MeshTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

