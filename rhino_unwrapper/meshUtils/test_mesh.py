import unittest
from rhino_unwrapper import transformations as trans
import mesh
import meshLoad
reload(mesh)
reload(trans)
reload(meshLoad)
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs


def setUpModule():
    print("---- mesh ----")

def tearDownModule():
    print("---- module torn down ----")
    remove_objects()

def remove_objects():
    rs.DeleteObjects(rs.AllObjects())

class MakeMeshTestCase(unittest.TestCase):

    def test_make_test_mesh(self):
        tMesh = mesh.make_test_mesh()
        self.assertIsInstance(tMesh,mesh.Mesh)

    def test_make_upright_mesh(self):
        uMesh = mesh.make_upright_mesh()
        self.assertIsInstance(uMesh,mesh.Mesh)

    def test_make_cube_mesh(self):
        cMesh = mesh.make_cube_mesh()
        self.assertIsInstance(cMesh,mesh.Mesh)

class MeshCutInfoTestCase(unittest.TestCase):

    def setUp(self):
        self.mesh = mesh.make_test_mesh()

    def test_set_cuts(self):
        cuts = [0,1,2]
        self.assertTrue(self.mesh.set_cuts(cuts))
        cuts = [-1]
        self.assertRaises(AssertionError,self.mesh.set_cuts,cuts)
        cuts = ['a','b']
        self.assertRaises(AssertionError,self.mesh.set_cuts,cuts)

    def test_get_cuts(self):
        #default myMesh has no cuts; empty list
        self.assertEqual([],self.mesh.get_cuts())
        cuts = [0,2]
        self.mesh.set_cuts(cuts)
        self.assertEqual(cuts,self.mesh.get_cuts())

    def test_mesh_cuts_sticking_around(self):
        remove_objects()
        jMesh = mesh.make_cube_mesh()
        selection0 = meshLoad.MeshGetter().getRandMesh() #only one mesh to get
        self.assertTrue(selection0.UserDictionary.ContainsKey(jMesh.cut_key))
        jMesh = mesh.Mesh(selection0)
        correct_cuts = [1,2,3]
        jMesh.set_cuts(correct_cuts)
        second_mesh = meshLoad.MeshGetter().getRandMesh()
        item = list(second_mesh.UserDictionary[jMesh.cut_key])
        self.assertEqual(correct_cuts,item)


    def test_is_cut_edge(self):
        cuts = [1,2]
        edge = 1
        self.mesh.set_cuts(cuts)
        self.assertTrue(self.mesh.is_cut_edge(edge))
        self.assertFalse(self.mesh.is_cut_edge(0))
        self.assertFalse(self.mesh.is_cut_edge(-1))

    def test_is_fold_edge(self):
        cuts = [1,4]
        edge = 7
        self.mesh.set_cuts(cuts)
        self.assertTrue(self.mesh.is_fold_edge(edge))
        self.assertFalse(self.mesh.is_fold_edge(1))
        self.assertFalse(self.mesh.is_fold_edge(0))

    def test_is_naked_edge(self):
        naked = 0
        surrounded = 2
        self.assertTrue(self.mesh.is_naked_edge(naked))
        self.assertFalse(self.mesh.is_naked_edge(surrounded))
        self.assertRaises(AssertionError,self.mesh.is_naked_edge,-1)

class MeshTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mesh = mesh.make_test_mesh()

    def test_get_frame_oriented_with_face_normals(self):
        newFrame = self.mesh.get_frame_oriented_with_face_normal(edge=0,face=2)
        o = (0,5,0)
        x = (0,-1,0)
        y = (1,0,0)
        correct_frame = trans.Frame.create_frame_from_tuples(o,x,y)
        newFrame.show()
        self.assertTrue(newFrame.is_equal(correct_frame))

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

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(MakeMeshTestCase))
    suite.addTest(loader.loadTestsFromTestCase(MeshTestCase))
    suite.addTest(loader.loadTestsFromTestCase(MeshDiplayerTestCase))
    suite.addTest(loader.loadTestsFromTestCase(MeshCutInfoTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
    #remove_objects()
