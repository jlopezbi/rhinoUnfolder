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

"""chang name to assign edgeWeights, implicit in methods available for topoEdges"""
def assignEdgeWeights(mesh):
  '''
  input:
    mesh = instance of Rhino.Geometry.Mesh()
  ouput:
    faces = list of Faces as MeshFace class (4.rhino3d.com/5/rhinocommon/)
    connFaces = list of tuples (edgeIdx,weight)
  '''
  faces = []
  thetaMax = -1
  for i in range(mesh.Faces.Count):
    faces.append(mesh.Faces.GetFace(i))
  edge_weights = []
  for i in range(mesh.TopologyEdges.Count):
    arrConnFaces = mesh.TopologyEdges.GetConnectedFaces(i)

    f0 = arrConnFaces.GetValue(0)
    f1 = arrConnFaces.GetValue(1)
    angWeight = calculateAngle(arrConnFaces,mesh)
    if angWeight > thetaMax:
      thetaMax = angWeight
    edge_weights.append((i,angWeight))
    #connFaces.append(tupleConnFaces)
  edge_weights = sorted(edge_weights,key=lambda tup: tup[1],reverse=False)
  #how to reverse order of sorting??


  #pretty2DListPrint(edge_weights)

  return faces,edge_weights,thetaMax

def calculateAngle(arrConnFaces,mesh):
  faceIdx0 = arrConnFaces.GetValue(0)
  faceIdx1 = arrConnFaces.GetValue(1)

  faceNorm0 = mesh.FaceNormals.Item[faceIdx0]
  faceNorm1 = mesh.FaceNormals.Item[faceIdx1]

  return rs.VectorAngle(faceNorm0,faceNorm1) #returns None on error