import unittest
import mesh
reload(mesh)
import Rhino.Geometry as geom

class MakeMeshTestCase(unittest.TestCase):
    def test_make_test_mesh(self):
        mesh.make_test_mesh()

    def test_make_upright_mesh(self):
        mesh.make_upright_mesh()

class MeshTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mesh = mesh.make_test_mesh()

    def test_get_set_of_edges(self):
        self.assertEqual(self.mesh.get_set_of_edges(),set(range(16)))

    def test_get_points_for_face(self):
        points = self.mesh.get_points_for_face(0)

    def test_get_oriented_TVerts_for_edge(self):
        tVerts =  self.mesh.get_oriented_TVerts_for_edge(0,2)
        self.assertEqual(tVerts, [1,0])
        tVerts =  self.mesh.get_oriented_TVerts_for_edge(11,3)
        self.assertEqual(tVerts, [7,4])
        self.assertRaises(AssertionError,self.mesh.get_oriented_TVerts_for_edge,0,76)

    def test_get_edges_and_orientation_for_face(self):
        edges,orientations = self.mesh.get_edges_and_orientation_for_face(faceIdx=0)
        correct_edges = [2,1,7]
        correct_orientation = [0,1,1]
        self.assertEqual(set(correct_edges),set(edges))
        self.assertEqual(correct_orientation,orientations)

    def test_get_edges_ccw_besides_base(self):
        edges = self.mesh.get_edges_ccw_besides_base(baseEdge=4,face=4)
        correct_list = [(5,False),(3,False)]
        self.assertEqual(edges,correct_list)
    
    def test_get_aligned_points(self):
        orientedEdge = (0,False)
        pntA,pntB = self.mesh.get_aligned_points(orientedEdge)
        self.assertTrue(pntA.Equals(geom.Point3f(0,5,0)))
        self.assertTrue(pntB.Equals(geom.Point3f(0,0,0)))

    
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
        self.meshDisplayer.displayFacesIdx()

    def test_displayNormals(self):
        self.meshDisplayer.displayNormals()

    def test_display_edge_direction(self):
        self.meshDisplayer.display_edge_direction(0)

    def test_display_edge_direction_IJ(self):
        self.meshDisplayer.display_edge_direction_IJ(0)

    def test_display_all_edges_direction_IJ(self):
        self.meshDisplayer.display_all_edges_direction_IJ()

#    def test_display_all_edges_direction(self):
#        self.meshDisplayer.display_all_edges_direction()

    def test_display_face_vert_ordering(self):
        self.meshDisplayer.display_face_vert_ordering(0)
    
    def test_display_all_face_vert_ordering(self):
        self.meshDisplayer.display_all_face_vert_ordering()

if __name__ == "__main__":
    suiteA = unittest.TestLoader().loadTestsFromTestCase(MeshTestCase)
    suiteB = unittest.TestLoader().loadTestsFromTestCase(MeshDiplayerTestCase)
    suiteC = unittest.TestLoader().loadTestsFromTestCase(MakeMeshTestCase)
    big_suite = unittest.TestSuite([suiteA,suiteB,suiteC])
    unittest.TextTestRunner(verbosity=2).run(big_suite)
