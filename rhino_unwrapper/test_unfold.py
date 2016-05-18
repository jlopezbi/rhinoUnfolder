import unittest
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs

import transformations as trans
import unfold
import Map
import Net
import meshUtils.meshLoad as meshLoad
import meshUtils.mesh as mesh

reload(meshLoad)
reload(Net)
reload(unfold)
reload(trans)
reload(mesh)
reload(Map)

def setUpModule():
    print("---- unfold ----")

def tearDownModule():
    print("---- module torn down ----")
    rs.DeleteObjects(rs.AllObjects())


def remove_objects():
    rs.DeleteObjects(rs.AllObjects())

class UnFolderTestCase(unittest.TestCase):
    def setUp(self):
        self.myMesh = mesh.make_cube_mesh()
        self.displayer = mesh.MeshDisplayer(self.myMesh)
        self.unfolder = unfold.UnFolder(self.myMesh)
        #self.displayer.displayFacesIdx()
        #self.displayer.displayEdgesIdx()
        
    def test_get_arbitrary_mesh_loc_raises_error(self):
        self.assertRaises(AssertionError,self.unfolder.get_arbitrary_mesh_loc)

    def test_get_arbitrary_mesh_loc_gets_valid(self):
        cuts = [3,4,10,7,2]
        self.myMesh.set_cuts(cuts)
        #self.displayer.display_edges(cuts)
        meshLoc = self.unfolder.get_arbitrary_mesh_loc()
        self.assertIn(meshLoc.face, self.myMesh.face_indices())
        self.assertIn(meshLoc.edge, self.myMesh.get_cuts())
        self.assertIn(meshLoc.edge, self.myMesh.getFaceEdges(meshLoc.face))

    def test_get_arbitrary_mesh_loc_needs_correct_cuts(self):
        self.myMesh.set_cuts([11])
        def getter(canditate_faces):
            return 0
        self.assertRaises(AssertionError,self.unfolder.get_arbitrary_mesh_loc,getter)

    def test_unfolds_all_segments(self):
        cuts = [4,3,10,11,6,5,8,0]
        self.myMesh.set_cuts(cuts)
        self.displayer.display_edges(cuts)
        self.unfolder.unfold()
        island0 = self.unfolder.net.get_island(0)
        island1 = self.unfolder.net.get_island(1)
        #NOTE: points below are dependent on the translate vectors!
        island0.translate(geom.Vector3d(10,0,0))
        island1.translate(geom.Vector3d(30,0,0))
        self.unfolder.net.display()
        points = [
            geom.Point3d(15,0,0), #0
            geom.Point3d(10,0,0), #1
            geom.Point3d(15,5,0), #2
            geom.Point3d(10,5,0), #3
            geom.Point3d(20,0,0), #4
            geom.Point3d(20,5,0), #5
            geom.Point3d(15,10,0), #6
            geom.Point3d(10,10,0), #7
            geom.Point3d(5,5,0), #8
            geom.Point3d(5,0,0) #9
        ]
        island0.has_same_points(points)
        points = [
            geom.Point3d(35,0,0), #0
            geom.Point3d(30,0,0), #1
            geom.Point3d(35,5,0), #2
            geom.Point3d(30,5,0), #3
            geom.Point3d(25,5,0), #4
            geom.Point3d(25,0,0), #5
        ]
        island1.has_same_points(points)
        

if __name__=='__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(UnFolderTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

