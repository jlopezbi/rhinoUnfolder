from transformations import *
from classes import FlatEdge

def initBasisInfo(mesh, origin):
  faceIdx = 0
  edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
  tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
  initBasisInfo = (faceIdx,edgeIdx,tVertIdx)
  return initBasisInfo

def layoutMesh(foldList, mesh):
  flatEdges = [list() for _ in xrange(mesh.TopologyEdges.Count)]

  origin = rs.WorldXYPlane()
  basisInfo = initBasisInfo(mesh, origin)
  toBasis = origin

  flatEdges = layoutFace(0,basisInfo,foldList,mesh,toBasis,flatEdges)
  return flatEdges

def layoutFace(depth,basisInfo,foldList,mesh,toBasis,flatEdges,flatVerts):
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
  assignFlatVerts(mesh,faceIdx,flatVerts,xForm)

  faceEdges = getFaceEdges(basisInfo[0],mesh)

  for edgeIndex in faceEdges:
    flatCoords = assignNewPntsToEdge(transformToFlat,edgeIndex,mesh)
    tVertIdxs = getTVerts(edgeIndex,mesh)
    flatEdge = FlatEdge(edgeIndex,flatCoords,tVertIdxs)
    flatEdge.faceIdxs.append(basisInfo[0])

    if (edgeIndex in foldList):
      if (not alreadyBeenPlaced(edgeIndex,flatEdges)):
        
        newBasisInfo = getNewBasisInfo(basisInfo,edgeIndex,mesh)
        newToBasis = getBasisFlat(flatCoords)

        flatEdge.type  = "fold"
        flatEdge.faceIdxs.append(newBasisInfo[0])
        flatEdges[edgeIndex].append(flatEdge)

        #RECURSE
        flatEdges = layoutFace(depth+1,newBasisInfo,foldList,mesh,newToBasis,flatEdges,flatVerts)

    else:
      if len(flatEdges[edgeIndex])==0:
        flatEdge.type  = "naked"
        flatEdges[edgeIndex].append(flatEdge)
      elif len(flatEdges[edgeIndex])==1:
        flatEdge.type = "cut"
        flatEdge.hasTab = True
        flatEdge.tabAngles = FlatEdge.getTabAngles(mesh,basisInfo[0],edgeIndex)
        flatEdge.setTabSide(flatEdges,basisInfo[1])
        flatEdges[edgeIndex].append(flatEdge)
        flatEdges[edgeIndex][0].type = "cut" #make sure to set both edges to cut 
  return flatEdges

def assignFlatVerts(mesh,faceIdx,flatVerts,xForm):
  faceTVerts = getTVertsForFace(mesh,faceIdx)
  for tVert in faceTVerts:
    if not alreadyBeenPlaced(tVert,flatVerts):
      point = mesh.TopologyVertices.Item[tVert]
      point.Transform(xForm)
      point.Z = 0.0
      flatVert = FlatVert(tVert,point,faceIdx)
      flatVerts[tVert].append(flatVert)


def alreadyBeenPlaced(testIdx,flatElements):
  return len(flatElements[testIdx]) > 0


def getNewBasisInfo(oldBasisInfo,testEdgeIdx, mesh):
  faceIdx,edgeIdx,tVertIdx = oldBasisInfo
  newFaceIdx = getOtherFaceIdx(testEdgeIdx,faceIdx,mesh)
  newEdgeIdx = testEdgeIdx
  newTVertIdx = mesh.TopologyEdges.GetTopologyVertices(testEdgeIdx).I #convention: useI
  return newFaceIdx,newEdgeIdx,newTVertIdx


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