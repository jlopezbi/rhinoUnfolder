from rhino_unwrapper.commands import unwrap
from rhino_unwrapper.visualization import displayMeshEdges
from rhino_unwrapper.rhino_inputs import *
from rhino_unwrapper import weight_functions
from rhino_unwrapper import buckling_strips

# -RunPythonScript ResetEngine RhinoUnwrapper.Unwrap_cmd

from inspect import getmembers, isfunction, isclass

def all_weight_functions():
  return [m for m in getmembers(weight_functions, isfunction)]

__commandname__ = "Unwrap"

def RunCommand():
  #TODO: let user set these variables
  holeRadius = 0.125/2.0
  tabAngle = math.pi/4.0 #45deg
  buckleScale = 1
  buckleRange = (1,0.001) #percent increase in face for buckling
  drawTabs = True
  drawFaceHoles = False

  targetVec = Rhino.Geometry.Vector3d(0,0,1)
  mesh = getMesh("Select mesh to unwrap")
  if not mesh: return
  mesh.Normals.ComputeNormals()
  mesh.FaceNormals.ComputeFaceNormals()
  mesh.FaceNormals.UnitizeFaceNormals()

  '''
  userCuts = getUserCuts(True)
  if userCuts == None: return
  print "user cuts:"
  print userCuts
  '''

  userCuts = set([2, 4, 6, 8, 10, 12, 14, 15, 18, 20, 22, 23, 24, 26, 27, 28, 34, 36, 38, 40, 43, 44, 46, 50, 51, 55, 57, 59, 62, 64, 65, 68, 69, 71, 73, 75, 77, 78, 82, 83, 86, 89, 91, 94, 96, 98, 103, 105, 107, 108, 111, 112, 115, 117, 118, 120, 122, 125, 128, 130, 132, 134, 136, 140, 142, 145, 147, 150, 151, 153, 156, 157, 159, 161, 162, 164, 168, 170, 173, 175, 177, 179, 180, 181, 183, 185, 186, 188, 191, 193, 194, 196, 198, 199, 201, 203, 204, 206, 211, 213, 215, 217, 218, 219, 221, 223, 224, 226, 228, 231])
  

  

  weightFunction = getOption(all_weight_functions(), "WeightFunction")

  if mesh and weightFunction:
    buckleVals = buckling_strips.assignValuesToFaces(targetVec,buckleRange,mesh)
    
    #buckling_strips.displayScaledNormals(mesh,buckleVals)
    dataMap,net,foldList = unwrap(mesh,userCuts,holeRadius,tabAngle,buckleScale,buckleVals,drawTabs,drawFaceHoles,weightFunction)
    net.findInitalSegments()
    
  #SEGMENTATION 

  while True:
    flatEdge,edgeIdx,strType = getNewEdge("select new edge on net or mesh",net,dataMap)
    if strType == 'fold' or strType == 'contested':
      basePoint = flatEdge.getMidPoint(net.flatVerts)
      xForm,point = getUserTranslate("Pick point to translate segment to",basePoint)
      if xForm and point:
        face = flatEdge.getFaceFromPoint(net,point) #the face on segment side of the picked edge
        print "face: ",
        print face
        segmentFaces = net.findSegment(flatEdge,face)
        # print "segment: ",
        # print segment
        net.copyAndReasign(mesh,dataMap,flatEdge,edgeIdx,segmentFaces,face)
        translatedEdges = net.translateSegment(segmentFaces,xForm)
        net.redrawSegment(translatedEdges,segmentFaces)
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
