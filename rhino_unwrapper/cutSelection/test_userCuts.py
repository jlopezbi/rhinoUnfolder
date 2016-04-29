import unittest
import userCuts
reload(userCuts)

class GetMeshEdgeTestCase(unittest.TestCase):

    def test_selects_a_mesh_edge(self):
        userCuts.getMeshEdge("select mesh edge",False,90)

if __name__ == "__main__":
    unittest.main(verbosity=2,module='test_userCuts',exit=False)

