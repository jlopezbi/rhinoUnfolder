import unittest
import Rhino.Geometry as geom
import transformations as trans
import mesh
reload(trans)
reload(mesh)

class FrameTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        o = geom.Point3d(1,1,0)
        x =  geom.Vector3d(3,0,0)
        y = geom.Vector3d(0,3,0)
        cls.frame = trans.Frame.create_frame_from_vectors(o,x,y)

    def test_unitized(self):
        unit =  1.0
        self.assertEqual(self.frame.plane.XAxis.Length,unit)
        self.assertEqual(self.frame.plane.YAxis.Length,unit)
        self.assertEqual(self.frame.plane.ZAxis.Length,unit)

    def test_show(self):
        #check that show() method sends correct messages
        self.frame.show()

    def test_catches_non_orthogonal(self):
        o = geom.Point3d(1,0,0)
        x = geom.Vector3d(1,0,0)
        y = geom.Vector3d(.1,0,1)
        self.assertRaises(AssertionError, trans.Frame.create_frame_from_vectors,o,x,y)

    def test_catches_non_unitized(self):
        o = geom.Point3d(1,0,0)
        x = geom.Vector3d(6,0,0)
        y = geom.Vector3d(0,6,0)
        plane = geom.Plane(o,x,y)
        bad_frame = trans.Frame(plane)
        bad_frame.plane.XAxis = geom.Vector3d(6,0,0)
        bad_frame.plane.YAxis = geom.Vector3d(0,6,0)
        bad_frame.plane.ZAxis = geom.Vector3d(0,0,6)
        self.assertRaises(AssertionError,bad_frame._check_unitized)

    def test_is_equal(self):
        o = geom.Point3d(1,1,0)
        x =  geom.Vector3d(6,0,0)
        y = geom.Vector3d(0,6,0)
        test_frame = trans.Frame.create_frame_from_vectors(o,x,y)
        self.assertTrue(self.frame.is_equal(test_frame))

class FrameOnMeshTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mesh = mesh.make_test_mesh()
        cls.meshDisplayer = mesh.MeshDisplayer(cls.mesh)
        cls.meshDisplayer.displayFacesIdx()
        cls.meshDisplayer.displayEdgesIdx()
        cls.meshDisplayer.displayTVertsIdx()
    
    def test_get_frame_on_mesh(self):
        mesh_location = (4,3)
        o = geom.Point3d(0,10,0)
        x = geom.Vector3d(0,-1,0)
        y = geom.Vector3d(1,0,0)
        correct_frame = trans.Frame.create_frame_from_vectors(o,x,y)
        frame = trans.get_frame_on_mesh(mesh_location,self.mesh)
        frame.show()
        self.assertTrue(frame.is_equal(correct_frame))



if __name__ == "__main__":
    suiteA = unittest.TestLoader().loadTestsFromTestCase(FrameTestCase)
    suiteB = unittest.TestLoader().loadTestsFromTestCase(FrameOnMeshTestCase)
    big_suite = unittest.TestSuite([suiteA,suiteB])
    unittest.TextTestRunner(verbosity=2).run(big_suite)

