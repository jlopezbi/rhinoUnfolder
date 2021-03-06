
#DEPRICATED: this functinoality is now in autoCuts.py!
def auto_fill_cuts(myMesh,user_cuts,weight_function):
    graph = buildMeshGraph(myMesh,user_cuts,weight_function)
    fold_list = getSpanningKruskal(graph,myMesh.mesh)
    filled_cut_list = getCutList(myMesh.mesh,fold_list)

def getSpanningKruskal(graph, mesh):
    '''
    this section of the code should be updated to use the union-find trick
    input:
      graph = contains faces and edge_weights
        faces = list of faces in mesh. necessary?
        edge_weights = list of tuples elem0 = edgeIdx, elem1 = weight
    output:
      foldList = list of edgeIdx's that are to be folded
    '''
    faces, edge_weights = graph
    treeSets = []
    foldList = []
    for tupEdge in edge_weights:
        edgeIdx = tupEdge[0]
        arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIdx)
        if(len(arrConnFaces) > 1):  # this avoids problems with naked edges
            setConnFaces = set(
                [arrConnFaces.GetValue(0), arrConnFaces.GetValue(1)])

            parentSets = []
            # print"edgeSet:"
            # print setConnFaces
            isLegal = True
            for i, treeSet in enumerate(treeSets):
                if setConnFaces.issubset(treeSet):
                    # print"--was illegal"
                    isLegal = False
                    break
                elif not setConnFaces.isdisjoint(treeSet):
                    # print"overlapped"
                    parentSets.append(i)

            if isLegal == True:
                foldList.append(edgeIdx)
                if len(parentSets) == 0:
                    treeSets.append(setConnFaces)
                elif len(parentSets) == 1:
                    treeSets[parentSets[0]].update(setConnFaces)
                elif len(parentSets) == 2:
                    treeSets[parentSets[0]].update(treeSets[parentSets[1]])
                    treeSets.pop(parentSets[1])
                elif len(parentSets) > 2:
                    print"Error in m.s.t: more than two sets overlapped with edgeSet!"
                    print "len parentSets: %d\n" % len(parentSets)
                    print(treeSets)
                    print(parentSets)
                    print(setConnFaces)

        # wow there must be a cleaner way of doing this!!! some set tricks
        # also the if staements could be cleaned up probs.
    return foldList

def getCutList(mesh, foldList):
    cutList = []
    for i in range(mesh.TopologyEdges.Count):
        if i not in foldList:
            cutList.append(i)
    return cutList

def meshFaces(mesh):
    return (mesh.Faces.GetFace(i) for i in xrange(mesh.Faces.Count))

def buildMeshGraph(myMesh, userCuts,weight_function):
    nodes = myMesh.meshFaces()
    edge_weights = []
    for i in xrange(myMesh.mesh.TopologyEdges.Count):
        if userCuts:
            if i not in userCuts:
                edge_weights.append((i,weight_function(myMesh, i)))
            else:
                edge_weights.append((i, float('inf')))
        else:
            edge_weights.append((i,weight_function(myMesh, i)))
    edge_weights = sorted(edge_weights, key=lambda tup: tup[1], reverse=False)
    # sorted from smallest to greatest
    return nodes, edge_weights
