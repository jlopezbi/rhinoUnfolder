import unittest
import Net
import transformations as trans
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs

reload(Net)
reload(trans)

def setUpModule():
    print("---- net ----")

def tearDownModule():
    print("---- module torn down ----")
    remove_objects()

def remove_objects():
    rs.DeleteObjects(rs.AllObjects())

class IslandTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.island = Net.Island()

    def setUp(self):
        self.island = Net.Island()

    def test_add_first_face_from_verts(self):
        self.island.add_vert_from_points(0.0,0.0,0.0) #0
        self.island.add_vert_from_points(5.0,0.0,0.0) #1
        self.island.add_vert_from_points(0.0,5.0,0.0) #2
        self.island.add_vert_from_points(5.0,5.0,0.0) #3
        face = self.island.add_first_face_from_verts(0,1,3,2)
        self.assertEqual(self.island.flatFaces[face].edges,[0,1,2,3])
        self.island.draw_edges()
        self.island.draw_faces()
        return face

    def test_breadth_construction(self):
        self.island.add_dummy_elements()
        #BASE EDGE
        pnt0 = geom.Point3d(5,6,0)
        pnt1 = geom.Point3d(5,10,0)
        self.island.add_vert_from_point(pnt0)
        self.island.add_vert_from_point(pnt1)
        # NOW ADD A NEW FACET
        pnt2 = geom.Point3d(7,6,0)
        pnt3 = geom.Point3d(7,8,0)
        self.island.layout_add_vert_point(pnt2)
        self.island.layout_add_edge(index=1)
        self.island.layout_add_vert_point(pnt3)
        self.island.layout_add_edge(index=2)
        self.island.layout_add_edge(index=3)
        self.island.layout_add_face(baseEdge=0)
        self.island.draw_all()

    def test_breadth_construction_catches_error(self):
        self.island.add_dummy_elements()
        self.assertRaises(AssertionError,self.island.layout_add_face,0)

    def test_update_edge_to_face(self):
        self.island.add_dummy_elements()
        self.island.update_edge_to_face(edge=0,toFace=1)
        self.assertEqual(self.island.flatEdges[0].toFace,1)

    def _test_add_face_from_edge_and_new_verts(self):
        self.test_add_first_face_from_verts()
        new_vert =  self.island.add_vert_from_points(10.0,0.0,0.0)
        edge = self.island.flatEdges[1]
        self.island.add_face_from_edge_and_new_verts(edge,[new_vert])
        new_verts = []
        new_verts.append(self.island.add_vert_from_points(5.0,10.0,0.0))
        new_verts.append(self.island.add_vert_from_points(4.0,7.0,0.0))
        new_verts.append(self.island.add_vert_from_points(0.0,10.0,0.0))
        edge = self.island.flatEdges[2]
        self.island.add_face_from_edge_and_new_verts(edge,new_verts)
        self.island.draw_edges()
        self.island.draw_verts()

    def test_transform(self):
        self.test_add_first_face_from_verts()
        self.island.draw_edges()
        self.island.clear()
        vec = geom.Vector3d(20.0,0.0,0.0) 
        self.island.translate(vec)
        self.island.draw_edges()

    def test_get_frame_reverse_edge(self):
        firstFace = self.test_add_first_face_from_verts()
        frame = self.island.get_frame_reverse_edge(edge=1,face=firstFace)
        frame.show()
        correct_frame = trans.Frame.create_frame_from_tuples((5,5,0),(0,-1,0),(1,0,0))
        self.assertTrue(correct_frame.is_equal(frame))

class StubbedIsland(object):
    def __init__(self):
        self.group_name = rs.AddGroup()
        self.line_guid = rs.AddLine((0,0,0),(5,5,0))
        rs.AddObjectToGroup(self.line_guid,self.group_name)

class NetTestCase(unittest.TestCase):
    def setUp(self):
        self.net = Net.Net()
        self.net.add_island(StubbedIsland())

    def test_get_island_for_line(self):
        islands = self.net.islands.values()
        correct_island = islands[0]
        line_guid = correct_island.line_guid
        island = self.net.get_island_for_line(line_guid)
        self.assertEqual(island,correct_island)



if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(IslandTestCase))
    suite.addTest(loader.loadTestsFromTestCase(NetTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
