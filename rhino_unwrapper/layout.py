
from transformations import *
from classes import FlatVert, FlatEdge, FlatFace
from Net import Net
from Map import Map
import math

def initBasisInfo(mesh, origin):
  #faceIdx = 0
  faceIdx = getLowestFace(mesh)
  edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
  tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
  initBasisInfo = (faceIdx,edgeIdx,tVertIdx)
  return initBasisInfo

#TODO: make the init face make sense: (the face closest to the xy plane)
#thats what the next two functions are about
def getLowestFace(mesh):
  lowestFace = (0,float('inf')) #(faceIdx,Zcoord)
  for i in range(mesh.Faces.Count):
    faceCenter = mesh.Faces.GetFaceCenter(i)
    Zcoord = math.fabs(faceCenter.Z)
    if Zcoord < lowestFace[1]:
      lowestFace = (i,Zcoord)
  return lowestFace[0]

def getLowestTVert(mesh,faceIdx):
  '''
  find the vertex on the given face that is closest to the origin
  '''
  tVerts = getTVertsForFace(mesh,faceIdx)
  origin = Rhino.Geometry.Point3f(0,0,0)
  lowest = (0,float('inf'))
  for tVert in tVerts:
    point = mesh.TopologyVertices[tVert] #point3f
    dist = point.DistanceTo(origin)
    if dist < lowest[1]:
      lowest = (tVert,dist)
  return lowest[0]


def layoutMesh(foldList, mesh,holeRadius,userCuts):
  origin = rs.WorldXYPlane()
  basisInfo = initBasisInfo(mesh, origin)
  toBasis = origin

  net = Net(mesh,holeRadius)
  dataMap = Map(mesh)
  net,dataMap = layoutFace(None,None,basisInfo,foldList,mesh,toBasis,net,dataMap,userCuts)
  return net,dataMap


def layoutFace(fromFace,hopEdge,basisInfo,foldList,mesh,toBasis,net,dataMap,userCuts):
  ''' Recurse through faces, hopping along fold edges
    input:
      fromFace = the face just came from in recursive traversal
      hopEdge = the face just hopped over from recursive traversal
      basisInfo = (faceIdx,edgeIdx,tVertIdx) information required to make basis
      foldList = list of edges that are folded
      mesh = mesh to unfold
      toBasis = basis in flat world
      net = data structure where flattened mesh is stored
      dataMap = data structure for mapping net elements to mesh elements
      userCuts = user defined cut edges
    out/in:
      net
      dataMap
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
    flatEdge.fromFace = basisInfo[0] #since faces have direct mapping this fromFace corresponds
                                     #to both the netFace and meshFace
    
    if edge in foldList:
      if not alreadyBeenPlaced(edge,dataMap.meshEdges):
        
        newBasisInfo = getNewBasisInfo(basisInfo,edge,mesh)
        newToBasis = getBasisFlat(flatEdge,net.flatVerts)

        if edge in userCuts:
          flatEdge.type = "contested"
          # if a flatEdge is contested then the next edge is going to be offset;
          # have unique netVertices -> the newToBasis is offset
        else:
          flatEdge.type  = "fold"

        flatEdge.toFace = newBasisInfo[0]
        netEdge = net.addEdge(flatEdge)
        dataMap.updateEdgeMap(edge,netEdge)

        #RECURSE
        recurse = True
        net,dataMap = layoutFace(basisInfo[0],flatEdge,newBasisInfo,foldList,mesh,newToBasis,net,dataMap,userCuts)

    else:
      if len(dataMap.meshEdges[edge])==0:
        flatEdge.type  = "naked"
        flatEdge.getTabFaceCenter(mesh,basisInfo[0],xForm)

        netEdge = net.addEdge(flatEdge)
        dataMap.updateEdgeMap(edge,netEdge)

      elif len(dataMap.meshEdges[edge])==1:
        flatEdge.type = "cut"
        
        #flatEdge.getTabAngles(mesh,basisInfo[0],xForm)
        #flatEdge.setTabSide(net)
        if flatEdge.getTabFaceCenter(mesh,basisInfo[0],xForm):
          flatEdge.hasTab = True
        
        netEdge = net.addEdge(flatEdge)
        dataMap.updateEdgeMap(edge,netEdge)
        sibling = dataMap.getSiblingNetEdge(edge,netEdge)
        sibFlatEdge = net.flatEdges[sibling]
        sibFlatEdge.type = "cut" #make sure to set both edges to cut 
        sibFlatEdge.hasTab = True #make sure to set both edges to cut 
        
        sibFlatEdge.pair = netEdge
        net.flatEdges[netEdge].pair = sibling
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
    hopMeshVerts = [net.flatVerts[netI].tVertIdx,net.flatVerts[netJ].tVertIdx]
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
        dataMap.meshVerts[tVert].append(netVert)
        netVerts.append(netVert)
        mapping[tVert]=netVert
      else:
        #this section is important for preserving order
        if tVert == net.flatVerts[netI].tVertIdx:
          netVerts.append(netI)
        elif tVert == net.flatVerts[netJ].tVertIdx:
          netVerts.append(netJ)
        pass
  return netVerts,mapping


def getNetEdges(mesh,edge,netVerts,dataMap):
  I,J = getTVertsForEdge(mesh,edge)
  vertI = dataMap.get


def transformPoint(mesh,tVert,xForm):
  point = Rhino.Geometry.Point3d(mesh.TopologyVertices.Item[tVert])
  point.Transform(xForm)
  point.Z = 0.0 #TODO: find where error comes from!!! (rounding?)
  return point

def alreadyBeenPlaced(edge,meshEdges):
  return len(meshEdges[edge])>0


def getNewBasisInfo(oldBasisInfo,testEdgeIdx, mesh):
  faceIdx,edgeIdx,tVertIdx = oldBasisInfo
  newFaceIdx = getOtherFaceIdx(testEdgeIdx,faceIdx,mesh)
  newEdgeIdx = testEdgeIdx
  newTVertIdx = mesh.TopologyEdges.GetTopologyVertices(testEdgeIdx).I #convention: useI
  return newFaceIdx,newEdgeIdx,newTVertIdx

