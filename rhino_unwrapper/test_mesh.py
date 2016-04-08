import unittest
import mesh
reload(mesh)

class MeshTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mesh = mesh.make_test_mesh()

    def test_get_set_of_edges(self):
        self.assertEqual(self.mesh.get_set_of_edges(),set(range(16)))

class MeshDiplayerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meshElementFinder = mesh.make_test_mesh()
        cls.meshDisplayer = mesh.MeshDisplayer(cls.meshElementFinder)

    def test_displayTVertIdx(self):
        self.meshDisplayer.displayTVertIdx(0)

    def test_displayTVertsIdx(self):
        self.meshDisplayer.displayTVertsIdx()

    def test_displayEdgeIdx(self):
        self.meshDisplayer.displayEdgeIdx(0)

    def test_displayEdgesIdx(self):
        self.meshDisplayer.displayEdgesIdx()

    def test_displayFaceIdxs(self):
        self.meshDisplayer.displayFaceIdxs()

if __name__ == "__main__":
    suiteA = unittest.TestLoader().loadTestsFromTestCase(MeshTestCase)
    suiteB = unittest.TestLoader().loadTestsFromTestCase(MeshDiplayerTestCase)
    big_suite = unittest.TestSuite([suiteA,suiteB])
    unittest.TextTestRunner(verbosity=2).run(big_suite)
