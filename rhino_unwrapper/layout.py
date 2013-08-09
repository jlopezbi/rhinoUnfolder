from transformations import *
from classes import FlatVert, FlatEdge, FlatFace

def initBasisInfo(mesh, origin):
  faceIdx = 0
  edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
  tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
  initBasisInfo = (faceIdx,edgeIdx,tVertIdx)
  return initBasisInfo

def layoutMesh(foldList, mesh):
  flatVerts = [list() for _ in xrange(mesh.TopologyVertices.Count)]
  flatEdges = [list() for _ in xrange(mesh.TopologyEdges.Count)]
  flatFaces = {}


  origin = rs.WorldXYPlane()
  basisInfo = initBasisInfo(mesh, origin)
  toBasis = origin

  flatEdges,flatVerts,flatFaces = layoutFace(None,None,basisInfo,foldList,mesh,toBasis,flatVerts,flatEdges,flatFaces)
  return flatVerts,flatEdges,flatFaces



def layoutFace(fromFace,hopEdge,basisInfo,foldList,mesh,toBasis,flatVerts,flatEdges,flatFaces):
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
  flatFaces[basisInfo[0]] = FlatFace(specifiers,fromFace)

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
        flatEdges,flatVerts,flatFaces = layoutFace(basisInfo[0],flatEdge,newBasisInfo,foldList,mesh,newToBasis,flatVerts,flatEdges,flatFaces)

    else:
      if len(flatEdges[edgeIndex])==0:
        flatEdge.type  = "naked"
        flatEdges[edgeIndex].append(flatEdge)
      elif len(flatEdges[edgeIndex])==1:
        flatEdge.type = "cut"
        flatEdge.hasTab = True
        flatEdge.getTabAngles(mesh,basisInfo[0],xForm)
        flatEdge.setTabSide(flatVerts,flatFaces)
        flatEdges[edgeIndex].append(flatEdge)
        flatEdges[edgeIndex][0].type = "cut" #make sure to set both edges to cut 
  return flatEdges, flatVerts, flatFaces

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
  seen = []
  for tVert in faceTVerts:
    if tVert not in seen: #avoid duplicates (triangle faces)
      seen.append(tVert)
      if tVert not in hopVerts:
        point = transformPoint(mesh,tVert,xForm)
        flatVert = FlatVert(tVert,point)
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