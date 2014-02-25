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
  drawFaces = False

  targetVec = Rhino.Geometry.Vector3d(0,0,1)
  mesh = getMesh("Select mesh to unwrap")
  if not mesh: return
  mesh.Normals.ComputeNormals()
  mesh.FaceNormals.ComputeFaceNormals()
  mesh.FaceNormals.UnitizeFaceNormals()

  #Use this to get user cuts and hard code that cut-set for debugging
  userCuts = getUserCuts(True)
  if userCuts == None: return
  print "user cuts:"
  print userCuts
  

  #userCuts = set([0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 15, 17, 20, 23, 27, 28, 30, 33, 35, 36, 37, 39, 41, 43, 47, 49, 52, 53, 54, 57, 59, 62, 65, 69, 72, 75, 77, 78, 80, 82, 85, 88, 91, 93, 95, 97, 100, 102, 104, 107, 109, 111, 113, 115, 117, 119, 121, 123, 125, 128, 131, 132, 134, 138, 141, 142, 144, 146, 147, 149, 153, 156, 158, 159, 160, 163, 165, 167, 170, 171, 172, 175, 176, 178, 179, 180, 183, 184, 185, 186, 188, 189, 190, 192, 195, 197, 198, 199, 200, 201, 202])
  
  

  
  

  

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
