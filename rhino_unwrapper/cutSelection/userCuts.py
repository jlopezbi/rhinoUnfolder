import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import System.Drawing
import System.Array
import math

#def all_weight_functions():
#    return dict([m for m in inspect.getmembers(wf, inspect.isfunction)])

def apply_user_cuts(rMesh,key,cutlist):
    '''
    stores cutList in the given rMesh, in a dictionary with key
    '''
    rMesh.UserDictionary.Set(key,System.Array[int](cutlist))

def get_user_cuts(myMesh,meshDisplayer):
    #NOTE: thinking about where this function should reside
    #TODO: avoid click-throughs.
    display = True # show selected cut edges
    edges = myMesh.get_set_of_edges()
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
                if isChain:
                    cuts.difference_update(myMesh.getChain(edgeIdx,angleTolerance))
                else:
                    cuts.difference_update([edgeIdx])

                if len(drawnEdges) != 0:
                    scriptcontext.doc.Objects.Delete(drawnEdges[edgeIdx], True)

            if display:
                for edgeIdx in drawnEdges.keys():
                    scriptcontext.doc.Objects.Delete(drawnEdges[edgeIdx], True)

                drawnEdges.update(meshDisplayer.display_edges(cuts,color))

        elif edgeIdx == -1:
            #print("enter:")
            print("set cuts")
            myMesh.set_cuts(list(cuts))
            break
    return cuts

def getMeshEdge(message, isChain, angle):
    getter= Rhino.Input.Custom.GetObject()
    getter.GeometryFilter = Rhino.DocObjects.ObjectType.MeshEdge
    getter.SetCommandPrompt(message)
    getter.AcceptNothing(True)

    boolOption = Rhino.Input.Custom.OptionToggle(isChain, "Off", "On")
    dblOption = Rhino.Input.Custom.OptionDouble(math.degrees(angle), 0, 180)

    getter.AddOptionDouble("maxAngle", dblOption)
    getter.AddOptionToggle("chainSelect", boolOption)

    edgeIdx = None
    mesh = None
    while True:
        getE =getter.Get()

        if getE == Rhino.Input.GetResult.Object:
            #TODO: figure out how to avoid selecting a obscured edge;
            #maybe use rs.IsVisibleInView(object_id) function;
            # add test line to doc, check if IsVisibleInView and if not
            # delete it and continue the loop
            objRef =getter.Object(0)
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
    getter.Dispose()

    isChain = boolOption.CurrentValue
    angle = math.radians(dblOption.CurrentValue)

    return (edgeIdx, isChain, angle, mesh)

def GetEdgeIdx(objref):
    # Rhino.DocObjects.ObjRef .GeometryComponentIndex to
    # Rhino.Geometry.ComponentIndex
    meshEdgeIndex = objref.GeometryComponentIndex

    return meshEdgeIndex.Index
