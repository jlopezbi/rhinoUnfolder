import unittest
import transformations as trans
import unfold
import mesh
import Map
reload(unfold)
reload(trans)
reload(mesh)
reload(Map)

class IslandCreatorTestCase(unittest.TestCase):
    """tests for IslandCreator class in unfold.py"""

    @classmethod
    def setUpClass(cls):
        cls.myMesh = mesh.make_upright_mesh()
        cls.meshDisplayer = mesh.MeshDisplayer(cls.myMesh)
        cls.meshDisplayer.display_all_elements()
        cls.dataMap = Map.Map(cls.myMesh)
        cls.meshLoc = unfold.MeshLoc(face=0,edge=1,tVert=0)
        cls.to_frame = trans.Frame.create_frame_from_tuples((0,-10,0),(1,0,0),(0,1,0)) 
        cls.to_frame.show()
        cls.islandCreator = unfold.IslandCreator(cls.dataMap,cls.myMesh,cls.meshLoc,cls.to_frame)

    def test_breadth_first_traversal(self):
        myMesh =  mesh.make_test_mesh()
        displayer = mesh.MeshDisplayer(myMesh)
        displayer.display_all_elements()
        path = unfold.breadth_first_traverse(myMesh,face=0)
        print "path of traverse: {}".format(path)

'''
    def test_add_first_edge_to_island(self):
        self.islandCreator.add_first_edge_to_island()
        #self.islandCreator.island.draw_verts()
        verts = self.islandCreator.island.flatVerts
        edges = self.islandCreator.island.flatEdges
        self.assertTrue(len(edges) == 1)
        self.assertTrue(len(verts) == 2)
        vertA = verts[0]
        vertB = verts[1]
        self.assertTrue(vertA.same_coordinates(0,-10,0))
        self.assertTrue(vertB.same_coordinates(5,-10,0))
        self.assertEqual(edges[0].fromFace, 0)
        self.assertEqual(edges[0].indexInFace, 0)
        '''

'''
    def test_add_facet_to_island_and_update_map(self):
        self.islandCreator.add_facet_to_island_and_update_map()

    def _test_assign_flat_verts(self):
        self.islandCreator.assign_flat_verts(self.meshLoc,self.to_frame,start=True)
        self.islandCreator.island.draw_verts()
        
    def _test_layout_face(self):
        self.islandCreator.layout_face(None,None,self.meshLoc,self.to_frame)
        '''


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(IslandCreatorTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
