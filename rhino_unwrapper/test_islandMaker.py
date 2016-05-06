import unittest,os
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs

import transformations as trans
import islandMaker as make
import meshUtils.mesh as mesh
import Map
import Net
import meshUtils.meshLoad as meshLoad

reload(mesh)
reload(Net)
reload(make)
reload(trans)
reload(mesh)
reload(Map)
 
def remove_objects():
    objs = rs.ObjectsByLayer('Default')
    rs.DeleteObjects(objs)

class StubbedIsland(object):

    def __init__(self):
        self.loc = geom.Point3d(-5.0,-5.0,0.0)
        self.xVec = geom.Vector3d(1.0,0.0,0.0)

    def get_frame_reverse_edge(self,edge,face):
        '''
        returns a frame located in the xy plane
        '''
        return trans.make_xy_frame(self.loc,self.xVec)

class StubbedMesh(object):

    def __init__(self):
        self.origin = geom.Point3d(3.0,3.0,3.0)
        self.normal = geom.Vector3d(0.0,0.0,1.0)
        self.x = geom.Vector3d(0.0,1.0,0.0)
        self.frame = trans.Frame.create_frame_from_normal_and_x(self.origin,
                                                               self.normal,
                                                               self.x) 
 
    def get_frame_oriented_with_face_normal(self,edge,face):
        return self.frame

    def get_point(self):
        u = 1.0
        v = 1.0
        return self.frame.plane.PointAt(u,v)

class IslandMakerTestCase(unittest.TestCase):

    def setUp(self):
        self.myMesh = mesh.make_upright_mesh()
        self.meshDisplayer = mesh.MeshDisplayer(self.myMesh)
        self.meshDisplayer.display_all_elements()
        self.island_idx = 0
        self.islandMaker = make.IslandMaker(None,self.myMesh,self.island_idx)

    def tearDown(self):
        remove_objects()

    def test_get_mapped_point(self):
        fakeMesh = StubbedMesh()
        self.islandMaker.island = StubbedIsland()
        self.islandMaker.myMesh = fakeMesh
        point = fakeMesh.get_point() 
        rs.AddPoint(point)
        meshLoc = make.MeshLoc(0,1)
        islandLoc = make.IslandLoc(0,0)
        mapped_point = self.islandMaker.get_mapped_point(point,meshLoc,islandLoc)
        rs.AddPoint(mapped_point)
        correct_point = geom.Point3d(-4.0,-4.0,0.0)
        self.assertTrue(mapped_point.Equals(correct_point))

    def test_layout_first_two_points(self):
        meshLoc = make.MeshLoc(face=0,edge=1)
        start_frame = trans.Frame.create_frame_from_tuples((0,-10,0),
                                                           (1,0,0),
                                                           (0,1,0))
        start_frame.show()
        self.islandMaker.layout_first_two_points(meshLoc,start_frame)
        pnt1_correct = geom.Point3d(0,-10,0)
        pnt0_correct = geom.Point3d(5,-10,0)
        self.islandMaker.island.draw_all()
        self.assertTrue(self.islandMaker.island.flatVerts[0].hasSamePoint(pnt0_correct))
        self.assertTrue(self.islandMaker.island.flatVerts[1].hasSamePoint(pnt1_correct))
    
    def test_meshLoc_must_be_on_a_cutEdge(self):
        meshLoc = make.MeshLoc(face=0,edge=1)
        cuts = [2]
        self.myMesh.set_cuts(cuts)
        self.assertRaises(AssertionError,self.islandMaker.make_island_cuts,meshLoc)

    def test_make_island(self):
        meshLoc = make.MeshLoc(face=0,edge=1)
        start_frame = trans.Frame.create_frame_from_tuples((10,0,0),
                                                           (1,0,0),
                                                           (0,1,0))
        start_frame.show()
        self.islandMaker.make_island(meshLoc,start_frame)
        self.islandMaker.island.draw_all()
        island = self.islandMaker.island
        pnt0_correct = geom.Point3d(15,0,0)
        pnt1_correct = geom.Point3d(10,0,0)
        pnt2_correct = geom.Point3d(10,5,0)
        pnt3_correct = geom.Point3d(15,5,0)
        self.assertTrue(island.flatVerts[0].hasSamePoint(pnt0_correct))
        self.assertTrue(island.flatVerts[1].hasSamePoint(pnt1_correct))
        self.assertTrue(island.flatVerts[2].hasSamePoint(pnt2_correct))
        self.assertTrue(island.flatVerts[3].hasSamePoint(pnt3_correct))

class ComplexIslandMakerTestCase(unittest.TestCase):

    def tearDown(self):
        #remove_objects()
        pass

    def test_unfolds_a_segment_of_cube(self):
        jMesh = mesh.make_cube_mesh()
        viewer=mesh.MeshDisplayer(jMesh)
        viewer.displayEdgesIdx()
        cuts = [3,4,10,11,6,5]
        jMesh.set_cuts(cuts)
        viewer.display_edges(cuts)
        self.islandMaker = make.IslandMaker(None,jMesh,0)
        meshLoc = make.MeshLoc(face=1,edge=4)
        island = self.islandMaker.make_island_cuts(meshLoc)
        island.draw_all()
        correct_points = [
            geom.Point3d(5,0,0),
            geom.Point3d(0,0,0),
            geom.Point3d(5,5,0),
            geom.Point3d(0,5,0),
            geom.Point3d(5,10,0),
            geom.Point3d(0,10,0)]
        self.check_has_same_verts(island,correct_points)


    def test_make_island_from_a_cube_with_cuts(self):
        jMesh = mesh.make_cube_mesh()
        viewer = mesh.MeshDisplayer(jMesh)
        viewer.displayEdgesIdx()
        cuts = [8,0,4,10,3,11,5]
        jMesh.set_cuts(cuts)
        viewer.display_edges(cuts)
        viewer.displayFacesIdx()
        self.islandMaker = make.IslandMaker(None,jMesh,0)
        meshLoc = make.MeshLoc(face=1,edge=4)
        start_frame = trans.Frame.create_frame_from_tuples((10,0,0),
                                                           (1,0,0),
                                                           (0,1,0))
        start_frame.show()
        island = self.islandMaker.make_island_cuts(meshLoc,start_frame)
        island.draw_all()
        correct_points = [
            geom.Point3d(15,0,0), #0    
            geom.Point3d(10,0,0), #1
            geom.Point3d(15,5,0), #2 
            geom.Point3d(10,5,0), #3 
            geom.Point3d(15,10,0), #4
            geom.Point3d(10,10,0), #5
            geom.Point3d(15,15,0), #6
            geom.Point3d(10,15,0), #7
            geom.Point3d(20,10,0), #8
            geom.Point3d(20,15,0), #9
            geom.Point3d(15,20,0), #10
            geom.Point3d(10,20,0), #11
            geom.Point3d(5,15,0), #12
            geom.Point3d(5,10,0) #13 ]
        ]
        self.check_has_same_verts(island,correct_points)

    def check_has_same_verts(self,island,correct_points):
        for i,vert in enumerate(island.flatVerts):
            self.assertTrue(vert.hasSamePoint(correct_points[i]))


    def _test_make_island_cone(self):
        meshFile = "/TestMeshes/cone"
        myMesh = mesh.Mesh(meshLoad.load_mesh(meshFile))
        displayer = mesh.MeshDisplayer(myMesh)
        displayer.display_all_elements()
        face = 0
        edge = myMesh.getFaceEdges(face)[0]
        island_idx = 0
        self.islandMaker = make.IslandMaker(None,myMesh,island_idx)

        meshLoc = make.MeshLoc(face,edge)
        start_frame = trans.Frame.create_frame_from_tuples((20,0,0),
                                                           (1,0,0),
                                                           (0,1,0))
        start_frame.show()
        island = self.islandMaker.make_island(meshLoc,start_frame)
        island.draw_all()
        #TODO: use assertions to check if layout actually worked

if __name__ == '__main__':
    #file_name = os.path.basename(__file__).split('.')[0]
    #unittest.main(verbosity=2,module=file_name,exit=False)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(IslandMakerTestCase))
    suite.addTest(loader.loadTestsFromTestCase(ComplexIslandMakerTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

