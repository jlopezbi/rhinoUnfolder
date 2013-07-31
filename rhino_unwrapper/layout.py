from transformations import *
from classes import FlatEdge, FlatVert

def initBasisInfo(mesh, origin):
  faceIdx = 0
  edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
  tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
  initBasisInfo = (faceIdx,edgeIdx,tVertIdx)
  return initBasisInfo

def layoutMesh(foldList, mesh):
  flatEdges = [list() for _ in xrange(mesh.TopologyEdges.Count)]
  flatVerts = [list() for _ in xrange(mesh.TopologyVertices.Count)]

  origin = rs.WorldXYPlane()
  basisInfo = initBasisInfo(mesh, origin)
  toBasis = origin

  flatEdges,flatVerts = layoutFace(None,basisInfo,foldList,mesh,toBasis,flatEdges,flatVerts)
  return flatEdges,flatVerts



'''
def netPointForMeshPoint(net, mesh, point):
  if point = netGetPoint(net, point): #this is not allowed in python. whats it called?
    return point
  else:
    netPoint = netCoordinates(net, point)
    return netAddPoint(netPoint, point)


def meshEdgeForNetEdge(net, edge):
  pass

def edgeAlreadyPlaced(net, edge):
  pass

def netAddEdge(net, edge):   
  for point in edge:
    netCoordinates(point, transform)


def edgeAlreadyPlaced(edge):
  pass

def isFoldEdge(foldList, edge):
  return edge in foldList

def isNakedEdge(mesh, edge):
  len(getFacesForEdge(mesh,edge)) < 2

def isCutEdge(mesh, foldList, edge):
  !isNakedEdge(mesh, edge) or !isFoldEdge(foldList, edge)

def place(mesh, newEdge):
  if isCutEdge(mesh, foldList, newEdge) or !edgeAlreadyPlaced(newEdge):
    netAddEdge(newEdge)

def neighboringFace(mesh, face, edge):
  connectedFaces = getFacesForEdge(mesh,edge)
  return (connectedFaces - face)[0]

def layout(mesh, foldList, face):
  for edge in face:
    place(mesh, foldList, edge)
    if foldEdge:
      neighbor = neighbordingFace(mesh, face, edge)
      layout(mesh, foldList, neighbor)







  # layoutFacePoints(face)

  # for edge in edgesForFace(face):
  #   if foldEdge:
  #     addsEdge to flatEdges (as fold)
  #     layout(newFace)
  #   else:
  #     addEdge to flatEdges (as cut or naked)

  # addEdge(edge,)

'''




def layoutFace(hopEdge,basisInfo,foldList,mesh,toBasis,flatEdges,flatVerts):
  ''' Recurse through faces, hopping along fold edges
    input:
      depth = recursion level
      basisInfo = (faceIdx,edgeIdx,tVertIdx) information required to make basis
      foldList = list of edges that are folded
      mesh = mesh to unfold
      toBasis = basis in flat world
    out/in:
      flatEdges = list containing flatEdges (a class that stores the edgeIdx,coordinates)
  '''
  xForm = getTransform(basisInfo,toBasis,mesh)
  specifiers = assignFlatVerts(mesh,hopEdge,basisInfo[0],flatVerts,xForm)

  faceEdges = getFaceEdges(basisInfo[0],mesh)

  for edgeIndex in faceEdges:
    tVertIdxs = getTVertsForEdge(mesh,edgeIndex)
    #tVertSpecs = getTVertSpecs(tVertIdxs,specifiers)
    flatEdge = FlatEdge(edgeIndex,tVertIdxs,specifiers)
    flatEdge.faceIdx = basisInfo[0]

    if (edgeIndex in foldList):
      if (not alreadyBeenPlaced(edgeIndex,flatEdges)):
        
        newBasisInfo = getNewBasisInfo(basisInfo,edgeIndex,mesh)
        newToBasis = getBasisFlat(flatEdge,flatVerts)

        flatEdge.type  = "fold"
        #flatEdge.faceIdxs.append(newBasisInfo[0])
        flatEdges[edgeIndex].append(flatEdge)

        #RECURSE
        flatEdges,flatVerts = layoutFace(flatEdge,newBasisInfo,foldList,mesh,newToBasis,flatEdges,flatVerts)

    else:
      if len(flatEdges[edgeIndex])==0:
        flatEdge.type  = "naked"
        flatEdges[edgeIndex].append(flatEdge)
      elif len(flatEdges[edgeIndex])==1:
        flatEdge.type = "cut"
        flatEdge.hasTab = True
        flatEdge.getTabAngles(mesh,basisInfo[0],xForm)
        flatEdge.setTabSide(flatEdges,basisInfo[1],flatVerts)
        flatEdges[edgeIndex].append(flatEdge)
        flatEdges[edgeIndex][0].type = "cut" #make sure to set both edges to cut 
  return flatEdges, flatVerts

def assignFlatEdges(mesh,faceIdx,foldList,flatVerts):
  pass

def getTVertSpecs(tVertIdxs,specifiers):
  '''
  assume correct order of tVerts
  '''
  tVertSpecs = []
  for tVert in tVertIdxs:
    tVertSpecs.append(specifiers[tVert])
  assert(len(tVertSpecs)==2)
  return tVertSpecs



def assignFlatVerts(mesh,hopEdge,face,flatVerts,xForm):
  '''
  add valid flatVerts to flatVerts list and also return
  a dict of specifiers 
  '''

  faceTVerts = getTVertsForFace(mesh,face)
  specifiers = {}
  if hopEdge == None:
    hopVerts = []
  else:
    hopVerts = hopEdge.tVertSpecs.keys()
  for tVert in faceTVerts:
    if tVert not in hopVerts:
      point = transformPoint(mesh,tVert,xForm)
      flatVert = FlatVert(tVert,point,face)
      flatVerts[tVert].append(flatVert)
      specifiers[tVert] = len(flatVerts[tVert])-1
    else:
      specifiers[tVert] = specifyHopVert(tVert,hopEdge)
  return specifiers

def specifyHopVert(tVert,hopEdge):
  if hopEdge == None:
    return 0
  tVerts = hopEdge.tVertSpecs.keys()
  assert(tVert in tVerts)
  return hopEdge.tVertSpecs[tVert]
  




def transformPoint(mesh,tVert,xForm):
  point = mesh.TopologyVertices.Item[tVert]
  point.Transform(xForm)
  point.Z = 0.0
  return point



def alreadyBeenPlaced(testIdx,flatElements):
  return len(flatElements[testIdx]) > 0





def getNewBasisInfo(oldBasisInfo,testEdgeIdx, mesh):
  faceIdx,edgeIdx,tVertIdx = oldBasisInfo
  newFaceIdx = getOtherFaceIdx(testEdgeIdx,faceIdx,mesh)
  newEdgeIdx = testEdgeIdx
  newTVertIdx = mesh.TopologyEdges.GetTopologyVertices(testEdgeIdx).I #convention: useI
  return newFaceIdx,newEdgeIdx,newTVertIdx

#def assignTVerts():

def assignNewPntsToEdge(xForm,edgeIdx,mesh):
  #output: list of new coords, Point3f, always in order of I,J
  indexPair = mesh.TopologyEdges.GetTopologyVertices(edgeIdx)
  idxI = indexPair.I
  idxJ = indexPair.J
  pI = mesh.TopologyVertices.Item[idxI] #these are point3f
  pJ = mesh.TopologyVertices.Item[idxJ]
  pI.Transform(xForm)
  pJ.Transform(xForm)
  #try out just setting z componenet to zero by defualt
  pI.Z = 0.0
  pJ.Z = 0.0
  #assert(pI.Z == 0), "pI.Z!=0"
  #assert(pJ.Z == 0), "pJ.Z!=0"
  return [pI,pJ]