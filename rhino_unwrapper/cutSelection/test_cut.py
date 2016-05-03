import unittest,sys
path = "/Users/josh/Library/Application Support/McNeel/Rhinoceros/Scripts/rhinoUnfolder/rhino_unwrapper/"
sys.path.append(path)
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs
import meshUtils.mesh as mesh
import meshUtils.meshLoad as meshLoad
import userCuts

reload(userCuts)
reload(mesh)

def setUpModule():
    print("USERCUTS")

def tearDownModule():
    print("MODULE TORN DOWN")
    rs.DeleteObjects(rs.AllObjects())

#NOTE: 
#Requirements:
#    * asks user to select edge => returns selected edges and mesh
#    * user can deselect edges
#    * user can use chain selection
#    * user can use chain deselection
#    * automatically fill in any missing edges needed to unfold
#    * can automatically fill in all edges if user makes no selection
#    * saves cut/fold info to this mesh
#    * displays cut/fold info dynamically as I make selection (feedback)
#    * if mesh already has cut/fold info displays it before user modification

class UserAssginCutsTestCase(unittest.TestCase):
    def setUp(self):
        self.myMesh = mesh.make_test_mesh()

    def tearDown(self):
        delete_all()

    def test_applies_cut_list_to_mesh(self):
        rMesh = meshLoad.load_mesh("/TestMeshes/blob")
        cutList = [0,1,2]
        key = 'cuts'
        userCuts.apply_user_cuts(rMesh,key,cutList)
        self.assertEqual(cutList,list(rMesh.UserDictionary.Item[key]))

    def test_updates_mesh_cut_list(self):
        rMesh = meshLoad.load_mesh("/TestMeshes/blob")
        #TODO: does this stuff reside in some sort of other object?
        #like meshSeamer.update_cuts(cuts)?
        #userCuts.update_cut_list(mesh,key,cuts)

class AutoAssignCutsTestCase(unittest.TestCase):
    pass


def check_user_setting_cuts():
    delete_all()
    myMesh = mesh.make_test_mesh()
    meshDisplayer = mesh.MeshDisplayer(myMesh)
    userCuts.get_user_cuts(myMesh,meshDisplayer)

def delete_all():
    rs.DeleteObjects(rs.AllObjects())
        
if __name__ == '__main__':
    check_user_setting_cuts()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(UserAssginCutsTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

