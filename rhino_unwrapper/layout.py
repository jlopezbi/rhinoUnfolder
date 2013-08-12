from transformations import *
from classes import FlatVert, FlatEdge, FlatFace
from Net import Net
from Map import Map

def initBasisInfo(mesh, origin):
  faceIdx = 0
  edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
  tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
  initBasisInfo = (faceIdx,edgeIdx,tVertIdx)
  return initBasisInfo

def layoutMesh(foldList, mesh):
  origin = rs.WorldXYPlane()
  basisInfo = initBasisInfo(mesh, origin)
  toBasis = origin

  net = Net()
  dataMap = Map(mesh)
  net,dataMap = layoutFace(None,None,basisInfo,foldList,mesh,toBasis,net,dataMap)
  return net,dataMap


def layoutFace(fromFace,hopEdge,basisInfo,foldList,mesh,toBasis,net,dataMap):
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
  netVerts,mapping = assignFlatVerts(mesh,dataMap,net,hopEdge,basisInfo[0],xForm)
  net.flatFaces[basisInfo[0]] = FlatFace(netVerts,fromFace)

  faceEdges = getFaceEdges(basisInfo[0],mesh)
  for edge in faceEdges:
    meshI,meshJ = getTVertsForEdge(mesh,edge)
    netI = mapping[meshI]
    netJ = mapping[meshJ]
    flatEdge = FlatEdge(edge,netI,netJ) 
    flatEdge.fromFace = basisInfo[0]
    
    if edge in foldList:
      if not alreadyBeenPlaced(edge,dataMap.meshEdges):
        
        newBasisInfo = getNewBasisInfo(basisInfo,edge,mesh)
        newToBasis = getBasisFlat(flatEdge,net.flatVerts)

        flatEdge.type  = "fold"
        flatEdge.toFace = newToBasis[0]
        netEdge = net.addEdge(flatEdge)
        dataMap.updateEdgeMap(edge,netEdge)

        #RECURSE
        recurse = True
        net,dataMap = layoutFace(basisInfo[0],flatEdge,newBasisInfo,foldList,mesh,newToBasis,net,dataMap)

    else:
      if len(dataMap.meshEdges[edge])==0:
        flatEdge.type  = "naked"
        netEdge = net.addEdge(flatEdge)
        dataMap.updateEdgeMap(edge,netEdge)

      elif len(dataMap.meshEdges[edge])==1:
        flatEdge.type = "cut"
        flatEdge.hasTab = True
        flatEdge.getTabAngles(mesh,basisInfo[0],xForm)
        flatEdge.setTabSide(net)
        netEdge = net.addEdge(flatEdge)
        dataMap.updateEdgeMap(edge,netEdge)
        sibling = dataMap.getSiblingNetEdge(edge,netEdge)
        net.flatEdges[sibling].type = "cut" #make sure to set both edges to cut 
  return net,dataMap



def assignFlatVerts(mesh,dataMap,net,hopEdge,face,xForm):
  '''
  add valid flatVerts to flatVerts list and also return
  a list of netVerts 
  '''

  faceTVerts = getTVertsForFace(mesh,face)
  netVerts = []
  hopMeshVerts = []
  mapping = {}


  if hopEdge!=None:
    netI,netJ = [hopEdge.I,hopEdge.J]
    hopNetVerts = [netI,netJ]
    hopMeshVerts = [net.flatVerts[netI].tVertIdx,net.flatVerts[netJ].tVertIdx]
    netVerts.extend(hopNetVerts)
    mapping[hopMeshVerts[0]] = netI
    mapping[hopMeshVerts[1]] = netJ

  seen = []
  for tVert in faceTVerts:
    if tVert not in seen: #avoid duplicates (triangle faces)
      seen.append(tVert)
      if tVert not in hopMeshVerts:
        point = transformPoint(mesh,tVert,xForm)
        flatVert = FlatVert(tVert,point)
        netVert = net.addVert(flatVert)
        #rs.AddTextDot(str(netVert),point)
        dataMap.meshVerts[tVert].append(netVert)
        netVerts.append(netVert)
        mapping[tVert]=netVert
      else:
        pass
  return netVerts,mapping


def getNetEdges(mesh,edge,netVerts,dataMap):
  I,J = getTVertsForEdge(mesh,edge)
  vertI = dataMap.get


def transformPoint(mesh,tVert,xForm):
  point = Rhino.Geometry.Point3d(mesh.TopologyVertices.Item[tVert])
  point.Transform(xForm)
  point.Z = 0.0
  return point

def alreadyBeenPlaced(edge,meshEdges):
  return len(meshEdges[edge])>0


def getNewBasisInfo(oldBasisInfo,testEdgeIdx, mesh):
  faceIdx,edgeIdx,tVertIdx = oldBasisInfo
  newFaceIdx = getOtherFaceIdx(testEdgeIdx,faceIdx,mesh)
  newEdgeIdx = testEdgeIdx
  newTVertIdx = mesh.TopologyEdges.GetTopologyVertices(testEdgeIdx).I #convention: useI
  return newFaceIdx,newEdgeIdx,newTVertIdx

