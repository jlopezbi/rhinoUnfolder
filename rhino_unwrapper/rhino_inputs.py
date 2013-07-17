import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System.Drawing
from classes import FlatEdge


def getNewEdge(message,flatEdges):
  ge = Rhino.Input.Custom.GetObject()
  # | is a bitwise or. documentation says can combine filters with 'bitwize combination'
  ge.GeometryFilter = Rhino.DocObjects.ObjectType.MeshEdge | Rhino.DocObjects.ObjectType.Curve
  ge.EnablePreSelect(False,False)
  ge.SetCommandPrompt(message)
  ge.Get()

  if ge.CommandResult() != Rhino.Commands.Result.Success:
    print('failed to get mesh edge or curve in getNewCut')
    return None, 'exit'

  objRef = ge.Object(0)
  curve = objRef.Curve()
  mesh = objRef.Mesh()
  
  if curve:
    print("selected a curve:")
    curve_id = objRef.ObjectId
    flatEdge = FlatEdge.getFlatEdge(flatEdges,'line_id',curve_id)
    if flatEdge:
      print(" corresponding to mesh edge " +str(flatEdge.edgeIdx))

      return flatEdge,flatEdge.type
    else:
      print(" not corresponding to a mesh edge")

      return None, 'invalid'
  elif mesh:
    edgeIdx = GetEdgeIdx(objRef)
    #print("selected mesh edge "+str(edgeIdx))
    flatEdge = flatEdges[edgeIdx][0]

    return flatEdge,flatEdge.type



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

def getFlatEdgePair(flatEdges,strField,value):
  '''
  self.edgeIdx = _edgeIdx
  self.coordinates = _coordinates
  self.line_id = None
  self.geom = []
  self.type = None
  self.faceIdx = None
    '''

  strField = strField.upper()
  if strField == 'EDGEIDX':
    assert(type(value)==int)
    for flatEdgePair in flatEdges:
      if flatEdgePair[0].edgeIdx == value:
        return flatEdgePair
  elif strField == 'LINE_ID':
    #assert guid?
    for flatEdgePair in flatEdges:
      if flatEdgePair[0].line_id == value:
        return flatEdgePair
  elif strField =='TYPE':
    assert(type(value)==str)
    for flatEdgePair in flatEdges:
      if flatEdgePair[0].type == value:
        return flatEdgePair
  else:
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