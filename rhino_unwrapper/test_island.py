import unittest
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs
import island
import distribute
import transformations as trans
reload(island)
reload(distribute)
reload(trans)

def setUpModule():
    print("---- island ----")

def tearDownModule():
    print("---- module torn down ----")
    remove_objects()

def remove_objects():
    rs.DeleteObjects(rs.AllObjects())

class IslandTestCase(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        remove_objects()

    def setUp(self):
        self.island = island.Island()
    
    def tearDown(self):
        self.island.clear()
 
    def test_make_triangulated_square_island(self):
        island.make_triangulated_square_island(self.island)
        self.island.draw_edges()

    def test_add_first_face_from_verts(self):
        island.make_five_by_five_square_island(self.island)
        face = 0
        self.assertEqual(self.island.flatFaces[face].edges,[0,1,2,3])
        self.island.draw_edges()
        self.island.draw_faces()

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
        island.make_five_by_five_square_island()
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
        island.make_five_by_five_square_island(self.island)
        self.island.draw_edges()
        self.island.clear()
        vec = geom.Vector3d(20.0,0.0,0.0) 
        self.island.translate(vec)
        self.island.draw_edges()

    def test_get_frame_reverse_edge(self):
        island.make_five_by_five_square_island(self.island)
        frame = self.island.get_frame_reverse_edge(edge=1,face=0)
        frame.show()
        correct_frame = trans.Frame.create_frame_from_tuples((5,5,0),(0,-1,0),(1,0,0))
        self.assertTrue(correct_frame.is_equal(frame))

class IslandAvoidTestCase(unittest.TestCase):

    def setUp(self):
        self.island = island.Island()

    def make_overlapping_islands(self):
        islandA = self.island
        islandB = island.Island()
        island.make_five_by_five_square_island(islandA)
        island.make_five_by_five_square_island(islandB)
        islandB.translate(geom.Vector3d(2,0,0))
        islandA.draw_edges()
        islandB.draw_edges()
        return islandA,islandB

    def test_get_boundary_polyline(self):
        #deprivated, since now in general not drwaing lines 
        #However, if needed can easily specifically draw cut lines
        island.make_five_by_five_square_island(self.island)
        self.island.clear()
        self.island.draw_edges()
        boundary = self.island.get_boundary_polyline()
        self.assertTrue(rs.IsPolyCurve(boundary))
        self.assertTrue(rs.IsCurveClosed(boundary))
        self.assertTrue(rs.IsCurvePlanar(boundary))
        self.island.clear()

    def test_is_overlapping(self):
        island_a,island_b = self.make_overlapping_islands()
        self.assertTrue(island_a.is_overlapping(island_b))
        island_b.translate(geom.Vector3d(10,0,0))
        island_b.clear()
        island_b.draw_edges()
        self.assertFalse(island_a.is_overlapping(island_b))
        self.assertFalse(island_b.is_overlapping(island_a))
        island_c = island.Island()
        island_c.add_vert_from_points(1.0,1.0,0.0) #0
        island_c.add_vert_from_points(4.0,1.0,0.0) #1
        island_c.add_vert_from_points(4.0,4.0,0.0) #2
        island_c.add_vert_from_points(1.0,4.0,0.0) #3
        face = island_c.add_first_face_from_verts(0,1,3,2)
        for edge in range(len(island_c.flatEdges)): island_c.change_to_cut_edge(edge)
        island_c.draw_edges()
        self.assertTrue(island_c.is_overlapping(island_a))
        self.assertTrue(island_a.is_overlapping(island_c))

        island_a.clear()
        island_b.clear()
        island_c.clear()

    def test_get_bounding_rectangle(self):
        island.make_five_by_five_square_island(self.island)
        self.island.draw_edges()
        rect = self.island.get_bounding_rectangle()
        self.island.clear()

    def test_move_to_edge(self):
        islandA,islandB = self.make_overlapping_islands()
        self.assertTrue(islandA.is_overlapping(islandB))
        islandA.move_to_edge(islandB)
        self.assertFalse(islandA.is_overlapping(islandB))

    def _test_avoid_other_island(self):
        '''depricated for now'''
        islandA,islandB = self.make_overlapping_islands()
        self.assertTrue(islandA.is_overlapping(islandB))
        islandA.avoid_other(islandB)
        self.assertFalse(islandA.is_overlapping(islandB))

class StubbedNet(object):
    def __init__(self,numIslands=5):
        self.islands = []
        for i in range(numIslands):
            new_island = island.Island()
            island.make_five_by_five_square_island(new_island)
            new_island.draw_edges()
            self.islands.append(new_island)

    def get_island_list(self):
        return self.islands

class DistributeTestCase(unittest.TestCase):
    '''
    I put the distribute test case in island since it already has the quite useful 
    island.make_five_by_five_square_island function
    '''
    def setUp(self):
        self.net = StubbedNet()

    def test_spread_out_islands_horizontally(self):
        distribute.spread_out_islands_horizontally(self.net)
        islands = self.net.islands
        for i,island in enumerate(islands[:-1]):
            self.assertFalse(island.is_overlapping(islands[i+1]))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(IslandTestCase))
    suite.addTest(loader.loadTestsFromTestCase(IslandAvoidTestCase))
    suite.addTest(loader.loadTestsFromTestCase(DistributeTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
