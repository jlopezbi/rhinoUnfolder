
def auto_fill_cuts(myMesh,user_cuts,weight_function):
    '''
    fill in user_cut list (or if empty create new one) which
    prefers edges with larger weight, given by the weight_function
    NOTE: currently sets naked edges as cuts
    '''
    sorted_edges = get_edge_weights(myMesh,user_cuts,weight_function)
    fold_list = getSpanningKruskal(sorted_edges,myMesh.mesh)
    cuts = getCutList(myMesh,fold_list)
    myMesh.set_cuts(cuts)

    return cuts

def get_edge_weights(myMesh, userCuts,weight_function):
    edges_with_weights= []
    for i in xrange(myMesh.mesh.TopologyEdges.Count):
        if userCuts:
            if i not in userCuts:
                edges_with_weights.append((i,weight_function(myMesh, i)))
            else:
                edges_with_weights.append((i, float('inf')))
        else:
            edges_with_weights.append((i,weight_function(myMesh, i)))
    return  edges_with_weights

def getSpanningKruskal(edges_with_weights, mesh):
    '''
    this section of the code should be updated to use the union-find trick. 
    input:
        edges_with_weights = list of tuples (edgeIdx,  weight) 
        mesh = Rhino.Geometry mesh
    output:
      foldList = list of edgeIdx's that are to be folded
    '''
    # sorted from smallest to greatest; user cuts, which get inf weight, have low likelyhood of becoming fold edges
    sorted_edges = sorted(edges_with_weights, key=lambda tup: tup[1], reverse=False)
    treeSets = []
    foldList = []
    for tupEdge in sorted_edges:
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
                #do not save edge as a fold if the user set it as a cut
                if tupEdge[1] != float('inf'):
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

def getCutList(myMesh, foldList):
    all_edges = myMesh.get_set_of_edges()
    cut_set = all_edges.difference(set(foldList))
    cut_list = []
    for edge in cut_set:
        if not myMesh.is_naked_edge(edge):
            cut_list.append(edge)
    return cut_list

