import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System.Drawing
import math
from visualization import displayMeshEdges


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


def getUserCuts(myMesh):
    display = True # show selected cut edges
    cuts = set()
    color = (0, 255, 0, 255)
    isChain = False
    angleTolerance = math.radians(30)  # inital defautl value
    drawnEdges = {}
    while True:
        edgeIdx, isChain, angleTolerance, mesh = getMeshEdge(
            "select cut edge on mesh", isChain, angleTolerance)

        if edgeIdx is None:
            #print("esc: edgeIDx is NONE")
            cuts = None
            break

        elif edgeIdx >= 0:
            #print("selected: valid edgeIdx")
            if edgeIdx not in cuts:
                if isChain:
                    cuts.update(myMesh.getChain(edgeIdx,angleTolerance))
                else:
                    cuts.update([edgeIdx])
            else:
                # if isChain:
               # cuts.difference_update(getChain(mesh,edgeIdx,angleTolerance))
                # else:
                cuts.difference_update([edgeIdx])

                if len(drawnEdges) != 0:
                    scriptcontext.doc.Objects.Delete(drawnEdges[edgeIdx], True)

            if display:
                for edgeIdx in drawnEdges.keys():
                    scriptcontext.doc.Objects.Delete(drawnEdges[edgeIdx], True)

                drawnEdges.update(myMesh.displayCutEdges(color, cuts, "cuts"))

        elif edgeIdx == -1:
            print("enter:")
            break

    return cuts


def getOptions_dict(options_dict):
    # Eventually would be nice to distiguish between cancel and enter keys
    texts = options_dict.keys()
    result = rs.ListBox(texts, message="select weight function", title="Title")
    option = texts[0]
    if result:
        option = result
    else:
        print "defualt"
    return options_dict[option]


def test_getOptionsRS():
    options = dict([("Three", 3), ("One", 1), ("Two", 2)])
    print getOptions_dict(options)

# DEPRICATED FOR NOW


def getOption(options, option_name, message=None):
    '''
      options = list of tuples (name, value)
      option_name = alphanumeric-only name for desired value
      message = message displayed above combo box in dialog
    '''
    getter = Rhino.Input.Custom.GetOption()
    getter.SetCommandPrompt(message)
    # getter.AcceptNothing(True)

    option_name = filter(str.isalnum, option_name)

    texts = [filter(str.isalnum, option[0]) for option in options]
    getter.AddOptionList(option_name, texts, 0)
    getter.SetDefaultInteger(0)

    getValue = getter.Get()
    print getter.CommandResult()

    if getter.GotDefault() == True:
        # default is the first function in weight_functions.py
        option = options[0][1]

    elif getValue == Rhino.Input.GetResult.Option:
        option = options[getter.Option().CurrentListOptionIndex][1]

    elif getValue == Rhino.Input.GetResult.Cancel:
        print("aborted command using escape key")
        return

    return option


def test_getOption():
    options = [("One", 1), ("Two", 2), ("Three", 3)]
    name = "TestOptiosn"
    chosenOption = getOption(options, name, "This is a Test Options Thing")
    print chosenOption


def getNewEdge(message, net, dataMap):
    ge = Rhino.Input.Custom.GetObject()
    # | is a bitwise or. documentation says can combine filters with 'bitwize combination'
    ge.GeometryFilter = Rhino.DocObjects.ObjectType.MeshEdge | Rhino.DocObjects.ObjectType.Curve
    ge.EnablePreSelect(False, False)
    ge.SetCommandPrompt(message)
    ge.Get()

    if ge.CommandResult() != Rhino.Commands.Result.Success:
        print('failed to get mesh edge or curve in getNewCut')
        return None, None, 'exit'

    objRef = ge.Object(0)
    curve = objRef.Curve()
    mesh = objRef.Mesh()

    if curve:
        print("selected a curve:")
        curve_id = objRef.ObjectId
        flatEdge, idx = net.getFlatEdgeForLine(curve_id)
        if flatEdge:
            print(" corresponding to mesh edge " + str(flatEdge.edgeIdx))

            return flatEdge, idx, flatEdge.type
        else:
            print(" not corresponding to a mesh edge")

            return None, 'invalid'
    elif mesh:
        edgeIdx = GetEdgeIdx(objRef)
        #print("selected mesh edge "+str(edgeIdx))
        flatEdge = None  # in this case there could be multiple flat edges
        return edgeIdx, flatEdge, flatEdge

    return flatEdge, idx, flatEdge.type


def getMeshEdge(message, isChain, angle):
    ge = Rhino.Input.Custom.GetObject()
    ge.GeometryFilter = Rhino.DocObjects.ObjectType.MeshEdge
    ge.SetCommandPrompt(message)
    ge.AcceptNothing(True)

    boolOption = Rhino.Input.Custom.OptionToggle(isChain, "Off", "On")
    dblOption = Rhino.Input.Custom.OptionDouble(math.degrees(angle), 0, 180)

    ge.AddOptionDouble("maxAngle", dblOption)
    ge.AddOptionToggle("chainSelect", boolOption)

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

    return (edgeIdx, isChain, angle, mesh)


def GetEdgeIdx(objref):
    # Rhino.DocObjects.ObjRef .GeometryComponentIndex to
    # Rhino.Geometry.ComponentIndex
    meshEdgeIndex = objref.GeometryComponentIndex

    return meshEdgeIndex.Index


def getUserTranslate(message, basePoint):
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
    vec = vecTo - vecFrom

    xForm = Rhino.Geometry.Transform.Translation(vec)
    return xForm, point

if __name__ == "__main__":
    test_getOptionsRS()
    # test_getOption()
