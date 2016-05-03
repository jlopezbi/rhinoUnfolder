import unittest,os
import cutSelection.userCuts as userCuts
import meshUtils.meshLoad as meshLoad
import meshUtils.mesh as mesh
reload(userCuts)
reload(meshLoad)


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

class GetMeshEdgeTestCase(unittest.TestCase):

    def test_selects_a_mesh_edge(self):
        userCuts.getMeshEdge("select mesh edge",False,90)

    def test_getUserCuts(self):
        print "AFADF"
        mesh = meshLoad.user_select_mesh()
        #NOTE myMesh not defined yet
        userCuts.getUserCuts(myMesh)
        print "mesh selected: {}".format(mesh)

if __name__ == "__main__":
    file_name = os.path.basename(__file__).split('.')[0]
    unittest.main(verbosity=2,module=file_name,exit=False)

