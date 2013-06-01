import rhinoscriptsyntax as rs

def getSpanningKruskal(faces,edge_weights,mesh):

  '''
  note: have not considered open mesh, or non-manifold edges
  input:
    faces = list of faces in mesh. necessary?
    edge_weights = list of tuples elem0 = edgeIdx, elem1 = weight
  output:
    foldList = list of edgeIdx's that are to be cut
  '''
  treeSets = []
  foldList = []
  for tupEdge in edge_weights:
    edgeIdx = tupEdge[0]
    arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIdx)
    setConnFaces = set([arrConnFaces.GetValue(0),arrConnFaces.GetValue(1)])


    parentSets = []
    #print"edgeSet:"
    #print setConnFaces
    isLegal = True
    for i, treeSet in enumerate(treeSets):
      if setConnFaces.issubset(treeSet):
        #print"--was illegal"
        isLegal = False
        break
      elif not setConnFaces.isdisjoint(treeSet):
          #print"overlapped"
          parentSets.append(i)

    if isLegal==True:
      foldList.append(edgeIdx)
      if len(parentSets) == 0:
        treeSets.append(setConnFaces)
      elif len(parentSets) == 1:
        treeSets[parentSets[0]].update(setConnFaces)
      elif len(parentSets) == 2:
        treeSets[parentSets[0]].update(treeSets[parentSets[1]])
        treeSets.pop(parentSets[1])
      elif len(parentSets)>2:
        print"Error in m.s.t: more than two sets overlapped with edgeSet!"
        print "len parentSets: %d\n" %len(parentSets)
        print(treeSets)
        print(parentSets)
        print(setConnFaces)


    # wow there must be a cleaner way of doing this!!! some set tricks
    # also the if staements could be cleaned up probs.
  return foldList

def connectedFaces(mesh, edgeIndex):
  arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(edgeIndex)

  faceIdx0 = arrConnFaces.GetValue(0)
  faceIdx1 = arrConnFaces.GetValue(1)

  return faceIdx0, faceIdx1

def edgeAngle(mesh, edgeIndex):
  faceIdx0, faceIdx1 = connectedFaces(mesh, edgeIndex)

  faceNorm0 = mesh.FaceNormals.Item[faceIdx0]
  faceNorm1 = mesh.FaceNormals.Item[faceIdx1]

  return rs.VectorAngle(faceNorm0,faceNorm1) # returns None on error

def meshFaces(mesh):
  return (mesh.Faces.GetFace(i) for i in xrange(mesh.Faces.Count))

def buildMeshGraph(mesh, weight):
  vertices = meshFaces(mesh)
  edge_weights = [(i, weight(mesh, i)) for i in xrange(mesh.TopologyEdges.Count)]

  edge_weights = sorted(edge_weights,key=lambda tup: tup[1],reverse=False)

  return vertices,edge_weights