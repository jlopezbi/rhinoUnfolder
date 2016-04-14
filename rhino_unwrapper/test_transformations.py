import unittest
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs
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
        mesh_location = (4,3,2)
        o = geom.Point3d(0,10,0)
        x = geom.Vector3d(0,-1,0)
        y = geom.Vector3d(1,0,0)
        correct_frame = trans.Frame.create_frame_from_vectors(o,x,y)
        frame = trans.get_frame_on_mesh(mesh_location,self.mesh)
        frame.show()
        self.assertTrue(frame.is_equal(correct_frame))

class TransformTestCase(unittest.TestCase):

    '''
    def test_change_basis_slick(self):
        #NOTE: This function was me playing around. Use this as reference
        #for creating a create_transform_matrix function that is more clear
        origin_frame = trans.Frame(geom.Plane.WorldXY)
        origin_frame.show()
        p = geom.Point3d(1,-2,1)
        u = geom.Vector3d(0,0,1)
        v = geom.Vector3d(1,0,0)
        to_frame = trans.Frame.create_frame_from_normal_and_x(p,u,v)
        to_frame.show()
        pnt = geom.Point3d(2,-1,1)
        original_pnt = geom.Point3d(pnt)
        rs.AddPoint(pnt)
        xForm1 = geom.Transform.ChangeBasis(origin_frame.plane,to_frame.plane)
        pnt.Transform(xForm1)
        rs.AddPoint(pnt)
        new_frame = trans.Frame.create_frame_from_normal_and_x(
            geom.Point3d(3,3,0),
            geom.Vector3d(1,0,0),
            geom.Vector3d(0,1,0))
        new_frame.show()
        xForm2 = geom.Transform.ChangeBasis(new_frame.plane,origin_frame.plane)
        original_pnt.Transform(xForm2*xForm1)
        rs.AddPoint(original_pnt)
    '''
    
    def test_get_mapped_point(self):
        from_frame = trans.Frame.create_frame_from_normal_and_x(
            origin = geom.Point3d(1,-2,1),
            normal = geom.Vector3d(0,0,1),
            x = geom.Vector3d(1,0,0))
        from_frame.show()
        to_frame = trans.Frame.create_frame_from_normal_and_x(
            origin = geom.Point3d(3,3,0),
            normal = geom.Vector3d(0,0,1),
            x = geom.Vector3d(-1,0,0))
        to_frame.show()
        pnt = geom.Point3d(2,-1,1)
        correct_point = geom.Point3d(2,2,0)
        new_point = trans.get_mapped_point(pnt,from_frame,to_frame)
        self.assertTrue(correct_point.Equals(new_point))
        rs.AddPoint(pnt)
        rs.AddPoint(new_point)
        rs.AddPoint(correct_point)

if __name__ == "__main__":
    suiteA = unittest.TestLoader().loadTestsFromTestCase(FrameTestCase) 
    suiteB = unittest.TestLoader().loadTestsFromTestCase(FrameOnMeshTestCase)
    suiteC = unittest.TestLoader().loadTestsFromTestCase(TransformTestCase)
    big_suite = unittest.TestSuite([suiteA,suiteB,suiteC])
    unittest.TextTestRunner(verbosity=2).run(suiteB)

