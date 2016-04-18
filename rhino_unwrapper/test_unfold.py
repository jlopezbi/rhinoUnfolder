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

    def test_assign_flat_verts(self):
        self.islandCreator.assign_flat_verts(self.meshLoc,self.to_frame,start=True)
        self.islandCreator.island.draw_verts()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(IslandCreatorTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
