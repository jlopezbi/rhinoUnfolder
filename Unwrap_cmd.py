from rhino_unwrapper.commands import unwrap
from rhino_unwrapper.segmentation import segmentNet
from rhino_unwrapper.visualization import displayMeshEdges
from rhino_unwrapper.rhino_inputs import *
from rhino_unwrapper import weight_functions

# -RunPythonScript ResetEngine RhinoUnwrapper.Unwrap_cmd

from inspect import getmembers, isfunction, isclass

def all_weight_functions():
  return [m for m in getmembers(weight_functions, isfunction)]

__commandname__ = "Unwrap"
def RunCommand( is_interactive ):
  mesh = getMesh("Select mesh to unwrap")
  if not mesh: return
  mesh.Normals.ComputeNormals()
  userCuts = getUserCuts()
  if userCuts == None: return
  print("usercuts:"),
  print userCuts
  #displayMeshEdges(mesh,(0,255,0,255),userCuts,"userCuts")
  weightFunction = getOption(all_weight_functions(), "WeightFunction")
  if mesh and weightFunction:
    flatEdges,flatVerts,foldList = unwrap(mesh, userCuts, weightFunction)

  while True:
    flatEdgeCut,strType = getNewEdge("select new edge on net or mesh",flatEdges)
    #print( str(type(flatEdgeCut)))
    if strType == 'fold':
      basePoint = flatEdgeCut.getMidPoint(flatVerts)
      xForm = getUserTranslate("Pick point to translate segment to",basePoint)
      if xForm:
        segmentNet(mesh,foldList,flatVerts,flatEdges,flatEdgeCut,xForm)
    elif strType == 'cut':
      break
    # elif strType == 'invalid':
    #   #print('invalid selection')
    elif strType == 'exit':
      break

  	




# def RunCommand( is_interactive ):
# 	mesh = rs.GetObject("Select mesh to unwrap",32,True,False)


if __name__=="__main__":
  RunCommand(True)