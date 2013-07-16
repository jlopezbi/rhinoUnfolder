from rhino_unwrapper.commands import unwrap, segmentNet
from rhino_unwrapper.rhino_helpers import getMesh, getOption, getUserCuts, getNewCut, getUserTranslate
from rhino_unwrapper.visualization import displayMeshEdges

from rhino_unwrapper import weight_functions

# -RunPythonScript ResetEngine RhinoUnwrapper.Unwrap_cmd

from inspect import getmembers, isfunction

def all_weight_functions():
  return [m for m in getmembers(weight_functions, isfunction)]

__commandname__ = "Unwrap"
def RunCommand( is_interactive ):
  mesh = getMesh("Select mesh to unwrap")
  userCuts = getUserCuts("Select edges to cut")
  weightFunction = getOption(all_weight_functions(), "WeightFunction")
  if mesh and weightFunction:
    flatEdges,foldList = unwrap(mesh, userCuts, weightFunction)

  edgeIdx,basePoint = getNewCut("select new cut edge",flatEdges)
  if type(edgeIdx)==int:

    xForm = getUserTranslate("Pick point to translate segment to",basePoint)
    segmentNet(mesh,foldList,flatEdges,edgeIdx,xForm)
  	




# def RunCommand( is_interactive ):
# 	mesh = rs.GetObject("Select mesh to unwrap",32,True,False)


if __name__=="__main__":
  RunCommand(True)