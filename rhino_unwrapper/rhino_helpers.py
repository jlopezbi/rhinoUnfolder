import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System.Drawing



def getNewCut(message,flatEdges):
  ge = Rhino.Input.Custom.GetObject()
  # | is a bitwise or. documentation says can combine filters with 'bitwize combination'
  ge.GeometryFilter = Rhino.DocObjects.ObjectType.MeshEdge | Rhino.DocObjects.ObjectType.Curve
  ge.EnablePreSelect(False,False)
  ge.SetCommandPrompt(message)
  ge.Get()

  if ge.CommandResult() != Rhino.Commands.Result.Success:
    print('failed to get mesh edge or curve in getNewCut')
    return None,None

  objRef = ge.Object(0)
  curve = objRef.Curve()
  mesh = objRef.Mesh()
  
  if curve:
    print("selected a curve:")
    curve_id = objRef.ObjectId
    midPnt = getMidPoint(curve_id)
    flatEdge = getFlatEdgeForCurve(curve_id,flatEdges)
    if flatEdge:
      print(" corresponding to mesh edge " +str(flatEdge.edgeIdx))
      return flatEdge,midPnt
    else:
      print(" no corresponding mesh edge")
      return None,None
  elif mesh:
    edgeIdx = GetEdgeIdx(objRef)
    print("selected mesh edge "+str(edgeIdx))
    return edgeIdx,Rhino.Geometry.Point3d(0,0,0)
  else:
    print("did not select anything valid")
    return None,None

def getFlatEdgeForCurve(curve_id,flatEdges):
  '''
  input:
    curve_id = guid to curve object
    flatEdges = list of lists which contain flatEdge objects:
      flatEdge.edgeIdx
              .coordinates
              .type
              .line_id
              .geom[]
  output:
    edgeIdx = the edgeIndex in the mesh that corresponeds to the given curve
    type = 
  '''
  #match curve_id to .geom
  for flatEdgeList in flatEdges:
    flatEdge = flatEdgeList[0]

    if len(flatEdgeList)>1:
      assert (flatEdgeList[0].type==flatEdgeList[1].type), "types for associated flatEdges are not equal"

    if curve_id == flatEdge.line_id:
      return flatEdge
  return

def getUserCuts(message=None):
  ge = Rhino.Input.Custom.GetObject()
  ge.GeometryFilter = Rhino.DocObjects.ObjectType.MeshEdge
  ge.SetCommandPrompt(message)
  ge.GetMultiple(0,0)

  if ge.CommandResult() != Rhino.Commands.Result.Success:
    print("no mesh edges selected as cuts for unwrapping")
    return

  objRefs = [ge.Object(i) for i in range(ge.ObjectCount)]
  edgeIdxs = [GetEdgeIdx(objref) for objref in objRefs] 
  mesh = objRefs[0].Mesh()

  return edgeIdxs


def GetEdgeIdx(objref):
  # Rhino.DocObjects.ObjRef .GeometryComponentIndex to Rhino.Geometry.ComponentIndex
  meshEdgeIndex = objref.GeometryComponentIndex
   
  return meshEdgeIndex.Index



def getOption(options, option_name, message=None):
  '''
    options = list of tuples (name, value)
    option_name = alphanumeric-only name for desired value
    message = message displayed above combo box in dialog
  '''
  getter = Rhino.Input.Custom.GetOption()
  getter.SetCommandPrompt(message)
  getter.AcceptNothing(True)

  option_name = filter(str.isalnum, option_name)

  texts = [filter(str.isalnum, option[0]) for option in options]
  getter.AddOptionList(option_name, texts, 0)
  getter.SetDefaultInteger(0)

  getValue = getter.Get()

  if getter.GotDefault() == True:
    option = options[0][1] #default is the first function in weight_functions.py

  elif getValue == Rhino.Input.GetResult.Option:
    option = options[getter.Option().CurrentListOptionIndex][1]

  elif getValue == Rhino.Input.GetResult.Cancel:
    print("aborted command using escape key")
    return

  return option

def getMesh(message=None):
  getter = Rhino.Input.Custom.GetObject()
  getter.SetCommandPrompt(message)
  getter.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh
  getter.SubObjectSelect = True
  getter.Get()
  if getter.CommandResult() != Rhino.Commands.Result.Success:
    return

  objref = getter.Object(0)
  obj = objref.Object()
  mesh = objref.Mesh()

  obj.Select(False)

  if obj:
    return mesh

def getUserTranslate(message,basePoint):
  '''
  basePoint can be point3d, Vector3d, Vector3f, or thee numbers(?)
  '''
  gp = Rhino.Input.Custom.GetPoint()
  #gp.DynamicDraw += DynamicDrawFunc
  gp.Get()
  if gp.CommandResult() != Rhino.Commands.Result.Success:
    return


  point = gp.Point()
  vecFrom = Rhino.Geometry.Vector3d(basePoint)
  vecTo = Rhino.Geometry.Vector3d(point)
  vec = vecTo-vecFrom

  xForm = Rhino.Geometry.Transform.Translation(vec)
  return xForm


def createGroup(groupName,objects):
  name = rs.AddGroup(groupName)
  if not rs.AddObjectsToGroup(objects,groupName):
    print "failed to group"
    return
  return name

def convertArray(array):
  pyList = []
  for i in range(array.Length):
    pyList.append(array.GetValue(i))
  return pyList

def getFacesForEdge(mesh, edgeIndex):
  '''
  returns an array of indices of the faces connected to a given edge
  if the array has only one face this inidicates it is a naked edge
  should be changed to get any number of faces, and return None if couldnt find 
  any faces
  '''
  arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIndex)

  faceIdxs = []
  faceIdxs.append(arrConnFaces.GetValue(0))
  if arrConnFaces.Length == 2:
    faceIdxs.append(arrConnFaces.GetValue(1))

  return faceIdxs

def getCenterPointLine(line):
  cenX = (line.FromX+line.ToX)/2
  cenY = (line.FromY+line.ToY)/2
  cenZ = (line.FromZ+line.ToZ)/2
  point = Rhino.Geometry.Point3d(cenX,cenY,cenZ)
  return point

def getFaceEdges(faceIdx,mesh):
  arrFaceEdges = mesh.TopologyEdges.GetEdgesForFace(faceIdx)
  return convertArray(arrFaceEdges)

def getTVerts(edgeIdx,mesh):
  vertPair = mesh.TopologyEdges.GetTopologyVertices(edgeIdx)
  return vertPair.I, vertPair.J

def getMedianEdgeLen(mesh):
  edgeLens = getEdgeLengths(mesh)
  return getMedian(edgeLens)

def getEdgeLengths(mesh):
  edgeLens = []
  for i in range(mesh.TopologyEdges.Count):
    edgeLine = mesh.TopologyEdges.EdgeLine(i)
    edgeLen = edgeLine.Length
    edgeLens.append(edgeLen)
  return edgeLens

def getEdgeLen(edgIdx,mesh):
  edgeLine = mesh.TopologyEdges.EdgeLine(edgeIdx)
  return edgeLine.Length

def getMidPoint(curve_id):
  '''get the midpoint of a curve
  '''
  startPnt = rs.CurveStartPoint(curve_id)
  endPnt = rs.CurveEndPoint(curve_id)

  cenX = (startPnt.X+endPnt.X)/2
  cenY = (startPnt.Y+endPnt.Y)/2
  cenZ = (startPnt.Z+endPnt.Z)/2
  point = Rhino.Geometry.Point3d(cenX,cenY,cenZ)

  return point

def getMedian(edgeLens):
  eLensSorted = sorted(edgeLens)
  nEdges = len(edgeLens)
  assert(nEdges>0), "nEdges is !>0, error in getMedianEdgeLen()"
  if nEdges%2 ==0:
    idxUpper = nEdges/2
    idxLower = idxUpper-1
    avg = (edgeLens[idxUpper]+edgeLens[idxLower])/2.0
    return avg
  else:
    return edgeLens[int(nEdges/2)]