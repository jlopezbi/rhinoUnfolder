import unittest
import Rhino
import transformations as trans
reload(trans)

class FrameTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        o = Rhino.Geometry.Vector3d(1,1,0)
        x =  Rhino.Geometry.Vector3d(3,0,0)
        z = Rhino.Geometry.Vector3d(0,0,3)
        cls.frame = trans.Frame.create_frame(o,x,z)

    def test_unitized(self):
        unit =  1.0
        self.assertEqual(self.frame.xVec.Length,unit)
        self.assertEqual(self.frame.yVec.Length,unit)
        self.assertEqual(self.frame.zVec.Length,unit)

    def test_show(self):
        #check that show() method sends correct messages
        self.frame.show()

    def test_catches_non_orthogonal(self):
        o = Rhino.Geometry.Vector3d(1,0,0)
        x = Rhino.Geometry.Vector3d(1,0,0)
        z = Rhino.Geometry.Vector3d(.1,0,1)
        self.assertRaises(AssertionError, trans.Frame.create_frame,o,x,z)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(FrameTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

