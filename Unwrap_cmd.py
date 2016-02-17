import rhino_unwrapper.commands as cm
import rhino_unwrapper.layout as la
import rhino_unwrapper.rhino_inputs as ri
import rhino_unwrapper.weight_functions as wf
import rhino_unwrapper.mesh as m
import inspect

reload(cm)
reload(la)
reload(ri)
reload(wf)
reload(m)


def all_weight_functions():
    return dict([m for m in inspect.getmembers(wf, inspect.isfunction)])


__commandname__ = "Unwrap"

def RunCommand():
    holeRadius = 0.125/2.0
    mesh = ri.getMesh("Select mesh to unwrap")
    if not mesh: return
    print "got a mesh: ",
    print mesh
    myMesh = m.Mesh(mesh)

    userCuts = ri.getUserCuts(myMesh)
    if userCuts == None: return

    print all_weight_functions()
    weightFunction = ri.getOptions_dict(all_weight_functions())

    if mesh and weightFunction:
        unfolder = la.UnFolder()
        dataMap,net,foldList = unfolder.unfold(myMesh,userCuts,weightFunction,holeRadius) net.findInitalSegments() net.drawEdges_simple() while True:
        flatEdge,idx = ri.get_new_cut("select new edge on net or mesh",net,dataMap)
        # TODO: figure out how to check type or isinstance of flatEdge -> cut
        # or fold
        if type(flatEdge) == 'FlatEdge.FoldEdge':
            basePoint = flatEdge.getMidPoint(net.flatVerts)
            xForm,point = ri.getUserTranslate("Pick point to translate segment to",basePoint)
            if xForm and point:
                face = flatEdge.getFaceFromPoint(net.flatFaces,net.flatVerts,point)
                print "face: ",
                print face
                segment = net.findSegment(flatEdge,face)
                # print "segment: ",
                # print segment
                net.copyAndReasign(dataMap,flatEdge,idx,segment,face)
                translatedEdges = net.translateSegment(segment,xForm)
                net.redrawSegment(translatedEdges)
                #net.updateCutEdge(flatEdge)


                #segmentNet(mesh,foldList,dataMap,net,flatEdge,face,xForm)
        elif type(flatEdge) == 'FlatEdge.CutEdge':
            pass
        elif flatEdge == None:
            break

# def RunCommand( is_interactive ):
#       mesh = rs.GetObject("Select mesh to unwrap",32,True,False)


if __name__=="__main__":
    RunCommand()
