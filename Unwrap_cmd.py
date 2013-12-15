from rhino_unwrapper.commands import unwrap
from rhino_unwrapper.visualization import displayMeshEdges
from rhino_unwrapper.rhino_inputs import *
from rhino_unwrapper import weight_functions

# -RunPythonScript ResetEngine RhinoUnwrapper.Unwrap_cmd

from inspect import getmembers, isfunction, isclass

def all_weight_functions():
  return [m for m in getmembers(weight_functions, isfunction)]

__commandname__ = "Unwrap"

def RunCommand():
  holeRadius = 0.125/2.0
  mesh = getMesh("Select mesh to unwrap")
  if not mesh: return
  mesh.Normals.ComputeNormals()

  userCuts = getUserCuts(True)
  if userCuts == None: return

  weightFunction = getOption(all_weight_functions(), "WeightFunction")

  if mesh and weightFunction:
    dataMap,net,foldList = unwrap(mesh, userCuts, holeRadius, weightFunction)
    net.findInitalSegments()
  #Get 

  while True:
    flatEdge,idx,strType = getNewEdge("select new edge on net or mesh",net,dataMap)
    if strType == 'fold':
      basePoint = flatEdge.getMidPoint(net.flatVerts)
      xForm,point = getUserTranslate("Pick point to translate segment to",basePoint)
      if xForm and point:
        face = flatEdge.getFaceFromPoint(net,point)
        print "face: ",
        print face
        segment = net.findSegment(flatEdge,face)
        # print "segment: ",
        # print segment
        net.copyAndReasign(mesh,dataMap,flatEdge,idx,segment,face)
        translatedEdges = net.translateSegment(segment,xForm)
        #net.updateCutEdge(flatEdge)
      

        #segmentNet(mesh,foldList,dataMap,net,flatEdge,face,xForm)
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
