import unittest
import Net
import Rhino.Geometry as geom

reload(Net)

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

    def test_add_face_from_edge_and_new_verts(self):
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

    def test_get_frame(self):
        self.clear_island()
        self.test_add_first_face_from_verts()
        print self.island.flatFaces[0].edges
        frame = self.island.get_frame(face=0,edge=0)
        frame.show()
        


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(IslandTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
