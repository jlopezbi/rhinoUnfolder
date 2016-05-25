import rhino_unwrapper.meshUtils.meshLoad as meshLoad
import rhino_unwrapper.meshUtils.mesh as mesh
import rhino_unwrapper.unfold as unfold
import rhino_unwrapper.distribute as distribute

'''
A script meant to be run on a mesh that already has 
cuts assigned
'''

uMesh = meshLoad.user_select_mesh()
jMesh = mesh.Mesh(uMesh)
displayer = mesh.MeshDisplayer(jMesh)

unfolder = unfold.UnFolder(jMesh)
net = unfolder.unfold()
net.display()

distribute.spread_out_islands_horizontally(net)




