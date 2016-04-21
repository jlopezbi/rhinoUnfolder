import unittest
import Net
import transformations as trans
import Rhino.Geometry as geom

reload(Net)
reload(trans)

class IslandTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.island = Net.Island()

    def clear_island(self):
        self.island = Net.Island()

    def test_add_first_face_from_verts(self):
        self.island.add_vert_from_points(0.0,0.0,0.0) #0
        self.island.add_vert_from_points(5.0,0.0,0.0) #1
        self.island.add_vert_from_points(0.0,5.0,0.0) #2
        self.island.add_vert_from_points(5.0,5.0,0.0) #3
        face = self.island.add_first_face_from_verts(0,1,3,2)
        #self.island.draw_edges()

    def test_tack_on_facet(self):
        self.clear_island()
        self.test_add_first_face_from_verts()
        Points = []
        Points.append(geom.Point3d(10.0,0.0,0.0))
        Points.append(geom.Point3d(10.0,5.0,0.0))
        face,edges = self.island.tack_on_facet(edge=1,points=Points)
        self.assertEqual(edges,[4,5,6])
        self.assertEqual(face,1)
        self.island.draw_edges()
        self.island.draw_faces()

    def _test_add_face_from_edge_and_new_verts(self):
        self.clear_island()
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
        self.clear_island()
        self.test_add_first_face_from_verts()
        self.island.draw_edges()
        vec = geom.Vector3d(20.0,0.0,0.0) 
        self.island.translate(vec)
        self.island.draw_edges()

    def test_get_frame_reverse_edge(self):
        self.clear_island()
        self.test_add_first_face_from_verts()
        frame = self.island.get_frame_reverse_edge(face=0,edge=1)
        frame.show()
        correct_frame = trans.Frame.create_frame_from_tuples((5,5,0),(0,-1,0),(1,0,0))
        self.assertTrue(correct_frame.is_equal(frame))
        


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(IslandTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
