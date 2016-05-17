import rhino_unwrapper.meshUtils.meshLoad as meshLoad
import rhino_unwrapper.meshUtils.mesh as mesh
import rhino_unwrapper.cutSelection.userCuts as userCuts
import rhino_unwrapper.cutSelection.autoCuts as autoCuts
import rhino_unwrapper.weight_functions as weight_functions
import rhino_unwrapper.unfold as unfold

#def all_weight_functions():
    #return dict([m for m in inspect.getmembers(weight_functions, inspect.isfunction)])

#hardcode a selection for wieght function for now
weight_function = weight_functions.edgeAngle

# SET UP MESH
uMesh = meshLoad.user_select_mesh()
jMesh = mesh.Mesh(uMesh)
displayer = mesh.MeshDisplayer(jMesh)

# SET CUTS
user_cuts = userCuts.get_user_cuts(jMesh,displayer)
cuts = autoCuts.auto_fill_cuts(jMesh,user_cuts,weight_function)
displayer.display_edges(cuts) #NOTE right now this will duplicate draw user-cuts

# UNFOLD

unfolder = unfold.UnFolder(jMesh)
unfolder.unfold()
unfolder.net.display()





