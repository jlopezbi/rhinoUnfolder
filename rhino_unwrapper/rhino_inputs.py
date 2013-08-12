import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System.Drawing
import math
from classes import FlatEdge
from rhino_helpers import getChain
from visualization import displayMeshEdges

def getNewEdge(message,net,dataMap):
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
    flatEdge = net.getFlatEdgeForLine(curve_id)
    if flatEdge:
      print(" corresponding to mesh edge " +str(flatEdge.edgeIdx))

      return flatEdge,flatEdge.type
    else:
      print(" not corresponding to a mesh edge")

      return None, 'invalid'
  elif mesh:
    edgeIdx = GetEdgeIdx(objRef)
    #print("selected mesh edge "+str(edgeIdx))
    flatEdge = None #in this case there could be multiple flat edges

    return flatEdge,flatEdge.type

def getUserCuts(disaply=True):
  cuts = []
  color = (0,255,0,255)
  isChain = False
  angleTolerance = math.radians(30) #inital defautl value
  while True:
    edgeIdx,isChain,angleTolerance,mesh = getMeshEdge("select cut edge on mesh",isChain,angleTolerance)

    if edgeIdx == None:
      #print("esc: edgeIDx is NONE")
      cuts = None
      break

    elif edgeIdx >= 0:
      #print("selected: valid edgeIdx")
      if edgeIdx not in cuts:
        if isChain:
          cuts.extend(getChain(mesh,edgeIdx,angleTolerance))
        else:
          cuts.append(edgeIdx)
      if display:
        displayMeshEdges(mesh,color,cuts,"cuts")
          
    elif edgeIdx == -1:
      print("enter:")
      break


  return cuts


def getMeshEdge(message,isChain,angle):
  ge = Rhino.Input.Custom.GetObject()
  ge.GeometryFilter = Rhino.DocObjects.ObjectType.MeshEdge
  ge.SetCommandPrompt(message)
  ge.AcceptNothing(True)

  boolOption = Rhino.Input.Custom.OptionToggle(isChain, "Off", "On")
  dblOption = Rhino.Input.Custom.OptionDouble(math.degrees(angle), 0, 180)

  ge.AddOptionDouble("maxAngle", dblOption)
  ge.AddOptionToggle("chainSelect", boolOption)
  
  ge.Get()
  edgeIdx = None
  mesh = None
  while True:
    getE = ge.Get()
    
    if getE == Rhino.Input.GetResult.Object:
      objRef = ge.Object(0)
      edgeIdx = GetEdgeIdx(objRef)
      mesh = objRef.Mesh()
      
    elif getE == Rhino.Input.GetResult.Option:
      continue
    elif getE == Rhino.Input.GetResult.Cancel:
      print("hit ESC in getMeshEdge()")
      edgeIdx = None
      break
    elif getE == Rhino.Input.GetResult.Nothing:
      print("hit ENTER in getMeshEdge()")
      edgeIdx = -1
      break
    break
  scriptcontext.doc.Objects.UnselectAll()
  ge.Dispose()

  isChain = boolOption.CurrentValue
  angle = math.radians(dblOption.CurrentValue)

  return (edgeIdx,isChain,angle,mesh)
#or do a while loop with options - select single edge - select edge


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
  return xForm,point