import rhino_unwrapper.commands as cm
import rhino_unwrapper.layout as la
import rhino_unwrapper.rhino_inputs as ri
import rhino_unwrapper.weight_functions as wf
import inspect


reload(wf)
reload(ri)
reload(cm)
reload(la)




def all_weight_functions():
    return dict([m for m in inspect.getmembers(wf, inspect.isfunction)])


__commandname__ = "Unwrap"

def RunCommand():
    holeRadius = 0.125/2.0
    mesh = ri.getMesh("Select mesh to unwrap")
    if not mesh: return
    mesh.Normals.ComputeNormals()

    userCuts = ri.getUserCuts(True)
    if userCuts == None: return

    print all_weight_functions()
    weightFunction = ri.getOptions_dict(all_weight_functions())

    if mesh and weightFunction:

        unfolder = la.UnFolder()
        dataMap,net,foldList = unfolder.unfold(mesh,userCuts,weightFunction,holeRadius)
        net.findInitalSegments()
        net.drawEdges_simple()
    #Get 

    while True:
        flatEdge,idx,strType = ri.getNewEdge("select new edge on net or mesh",net,dataMap)
        if strType == 'fold':
            basePoint = flatEdge.getMidPoint(net.flatVerts)
            xForm,point = ri.getUserTranslate("Pick point to translate segment to",basePoint)
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
#       mesh = rs.GetObject("Select mesh to unwrap",32,True,False)


if __name__=="__main__":
    RunCommand()
