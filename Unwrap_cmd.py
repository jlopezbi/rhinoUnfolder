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
  drawTabs = False
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

  #HACK FOR LG: set user cuts:
  userCuts = set([3, 5, 7, 9, 11, 14, 17, 21, 25, 29, 31, 32, 37, 39, 41, 42, 43, 48, 49, 50, 51, 54, 58, 60, 63, 64, 66, 68, 69, 71, 79, 80, 82, 83, 86, 87, 90, 91, 95, 99, 100, 101, 102, 106, 108, 110, 111, 113, 115, 116, 117, 118, 120, 122, 124, 128, 130, 132, 136, 139, 141, 142, 144, 145, 147, 149, 151, 155, 157, 159, 161, 165, 167, 169, 171, 173, 174, 176, 178, 181, 184, 186, 190, 192, 194, 196, 198, 200, 201, 203, 205, 209, 211, 214, 217, 219, 221, 223, 225, 226, 228, 230, 234, 236, 238, 240, 242, 244, 245, 247, 250, 252, 257, 259, 261, 263, 265, 267, 269, 271, 272, 274, 279, 282, 284, 286, 288, 290, 292, 294, 296, 298, 299, 303, 305, 308, 311, 313, 315, 317, 319, 321, 323, 325, 326, 330, 332, 336, 338, 340, 342, 344, 346, 350, 352, 353, 355, 357, 359, 363, 365, 367, 369, 373, 375, 377, 379, 380, 382, 384, 386, 390, 394, 396, 398, 400, 402, 404, 406, 407, 409, 411, 413, 419, 421, 423, 425, 427, 429, 431, 433, 434, 436, 438, 441, 443, 446, 449, 451, 455, 456])

  weightFunction = getOption(all_weight_functions(), "WeightFunction")

  if mesh and weightFunction:
    buckleVals = buckling_strips.assignValuesToFaces(targetVec,buckleRange,mesh)
    print 'buckleVal 0:',
    print buckleVals[0]
    buckling_strips.displayScaledNormals(mesh,buckleVals)
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
