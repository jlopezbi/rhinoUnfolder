import unittest,sys
path = "/Users/josh/Library/Application Support/McNeel/Rhinoceros/Scripts/rhinoUnfolder/rhino_unwrapper/"
path_meshUtils = "/Users/josh/Library/Application Support/McNeel/Rhinoceros/Scripts/rhinoUnfolder/rhino_unwrapper/meshUtils"
sys.path.append(path)
#sys.path.append(path_meshUtils)
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs
import meshUtils.mesh as mesh
import meshUtils.meshLoad as meshLoad
import userCuts
import autoCuts

reload(userCuts)
reload(autoCuts)
reload(mesh)
reload(meshLoad)

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

class UserAssignCutsTestCase(unittest.TestCase):
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

def weight_function(myMesh,edge):
    return 1.0

class AutoCutsTestCase(unittest.TestCase):
    def setUp(self):
        self.myMesh = mesh.make_test_mesh()

    def test_auto_generates_cuts(self):
        user_cuts = []
        cuts = autoCuts.auto_fill_cuts(self.myMesh,user_cuts,weight_function)
        displayer = mesh.MeshDisplayer(self.myMesh)
        #displayer.display_edges(cuts)
        self.assertEqual(cuts,[12])

    def test_auto_honors_user_cuts(self):
        user_cuts = [4]
        auto_cuts = autoCuts.auto_fill_cuts(self.myMesh,user_cuts,weight_function)
        displayer = mesh.MeshDisplayer(self.myMesh)
        self.assertEqual(auto_cuts,user_cuts)

    def test_auto_honors_loops_of_user_cuts(self):
        cuts = [4,3,7,10]
        cube_mesh = mesh.make_cube_mesh()
        displayer = mesh.MeshDisplayer(cube_mesh)
        displayer.displayEdgesIdx()
        auto_cuts = autoCuts.auto_fill_cuts(cube_mesh,cuts,weight_function)
        #TODO: make so assertion raises more descriptive error
        self.assertTrue(set(auto_cuts).issuperset(set(cuts)))
        displayer.display_edges(auto_cuts)

    def _test_auto_generates_cuts_on_blob(self):
        bMesh = mesh.Mesh(meshLoad.load_mesh("/TestMeshes/blob"))
        cuts = autoCuts.auto_fill_cuts(bMesh,[],weight_function)
        displayer = mesh.MeshDisplayer(bMesh)
        displayer.display_edges(cuts)
        #TODO: assertion > min spann forest or something

def check_user_setting_cuts():
    '''
    for testing user interaction
    '''
    delete_all()
    myMesh = mesh.make_test_mesh()
    meshDisplayer = mesh.MeshDisplayer(myMesh)
    userCuts.get_user_cuts(myMesh,meshDisplayer)

def delete_all():
    rs.DeleteObjects(rs.AllObjects())
        
if __name__ == '__main__':
    #check_user_setting_cuts()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    #suite.addTest(loader.loadTestsFromTestCase(UserAssignCutsTestCase))
    suite.addTest(loader.loadTestsFromTestCase(AutoCutsTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

