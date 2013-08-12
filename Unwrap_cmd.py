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

def RunCommand():
  mesh = getMesh("Select mesh to unwrap")
  if not mesh: return
  mesh.Normals.ComputeNormals()

  userCuts = getUserCuts(True)
  if userCuts == None: return

  weightFunction = getOption(all_weight_functions(), "WeightFunction")

  if mesh and weightFunction:
    dataMap,net,foldList = unwrap(mesh, userCuts, weightFunction)

  while True:
    flatEdge,strType = getNewEdge("select new edge on net or mesh",net,dataMap)
    #print( str(type(flatEdgeCut)))
    if strType == 'fold':
      basePoint = flatEdge.getMidPoint(net.flatVerts)
      xForm,point = getUserTranslate("Pick point to translate segment to",basePoint)
      if xForm:
        #net.segment(flatEdge,xForm,point)
        segmentNet(mesh,foldList,net.flatVerts,net.flatEdges,net.flatFaces,flatEdge,xForm)
    elif strType == 'cut':
      break
    # elif strType == 'invalid':
    #   #print('invalid selection')
    elif strType == 'exit':
      break

  	




# def RunCommand( is_interactive ):
# 	mesh = rs.GetObject("Select mesh to unwrap",32,True,False)


if __name__=="__main__":
  RunCommand()
