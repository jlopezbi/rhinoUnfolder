'''
buckling_strips:

stretch faces so that when they are attached at the seams to the original mesh the material is forced to buckle
for biome lunar gala project feb 2014
'''

import rhinoscriptsyntax as rs
import Rhino
import math
from rhino_helpers import *
from visualization import *


def viewFaceBuckles():
  mesh = getMesh("select mesh to view normals")
  mesh.FaceNormals.ComputeFaceNormals()
  mesh.FaceNormals.UnitizeFaceNormals()
  #draw a normal at the center of each face,
  #len proportional to the closeness to a targetVec (i.e. unit z)
  targetVec = Rhino.Geometry.Vector3d(0,0,1)
  #pointsForNormal = rs.GetPoints(True,False,'select base point','select end point',2)
  #planeNormal = Rhino.Geometry.Vector3d(pointsForNormal[1]-pointsForNormal[0])
  planeNormal = Rhino.Geometry.Vector3d(1,0,0)
  values = assignValuesToFaces(targetVec,mesh)
  #displayScaledNormals(mesh,values)
  #isplayAlginedEdges(mesh,planeNormal)
  displayBuckles(mesh,values,planeNormal)

def displayScaledNormals(mesh,values):
  #display face normals, whose length is proportional to the nearness (in terms of angle)
  #of the face normal to the target Vec
  for i in range(mesh.Faces.Count):
    faceNormal = mesh.FaceNormals[i] 
    displayVec = faceNormal.Multiply(faceNormal,values[i])
    faceCenter = mesh.Faces.GetFaceCenter(i) #Point3d
    newLoc = rs.VectorAdd(faceCenter, displayVec)
    feedLine = rs.AddLine(faceCenter,newLoc)

def displayBuckles(mesh,values,planeNormal):
  for faceIdx in range(mesh.Faces.Count):
    edgeIdx = getAlignedEdge(mesh,faceIdx,planeNormal)
    #addBucklesCurve(mesh,edgeIdx,faceIdx,values[faceIdx])
    addBuckleSurf(mesh,edgeIdx,faceIdx,values[faceIdx])

def addBuckleSurf(mesh,edgeIdx,faceIdx,buckleFactor):
  neighA,neighB = getNeighborEdges(mesh,edgeIdx,faceIdx)
  pointsA,pointsB = getNeighborEdgeLines(mesh,neighA[0],faceIdx)
  profileA = getBuckleCurve(mesh,pointsA,faceIdx,buckleFactor)
  profileB = getBuckleCurve(mesh,pointsB,faceIdx,buckleFactor)

  rs.AddLoftSrf([profileA,profileB], loft_type = 3) 

def addBucklesCurve(mesh,edgeIdx,faceIdx,buckleFactor):
  group = rs.AddGroup()
  geom = []
  points = getPointsForEdge(mesh,edgeIdx)
  curve = getBuckleCurve(mesh,points,faceIdx,buckleFactor)
  geom.append(scriptcontext.doc.Objects.AddCurve(curve))

def getBuckleCurve(mesh,points,faceIdx,buckleFactor):
 #       C
 #      / \
 # A---B   D---E

  scale = 1
  faceNormal = mesh.FaceNormals[faceIdx]

  pntA,pntE = points #point3f (i think)
  pntA = Rhino.Geometry.Point3d(pntA)
  pntE = Rhino.Geometry.Point3d(pntE)

  bVec = pntE-pntA
  dVec = pntA-pntE

  bVec = bVec*(1.0/5)
  dVec = dVec*(1.0/5)

  pntB = Rhino.Geometry.Point3d.Add(pntA,bVec)
  pntD = Rhino.Geometry.Point3d.Add(pntE,dVec)

  edgeVec = getVectorForPoints(pntA,pntE)
  edgeCenter = getMidPointBetweenPoints(pntA,pntE)

  buckleRepresent = scale*buckleFactor*edgeVec.Length
  offsetVec = faceNormal.Multiply(faceNormal,buckleRepresent)
  pntC = Rhino.Geometry.Point3d.Add(edgeCenter,offsetVec)

  points = [pntA,pntB,pntC,pntD,pntE]
  return Rhino.Geometry.NurbsCurve.Create(False,3,points)  

def displayAlginedEdges(mesh,planeNormal):
  color = (0,237,43,120) #red
  for i in range(mesh.Faces.Count):
    edge = getAlignedEdge(mesh,i,planeNormal)
    drawMeshEdge(mesh,edge,color,'EndArrowhead')

def getAlignedEdge(mesh,face,planeNormal):
  '''
  NOTE: this is hacky: it just so happens to work well for the sleeve for lg jacket!
  in other cases not so!
  '''
  faceEdges = getFaceEdges(face,mesh)
  #alignedEdge = (0,float('inf'))
  alignedEdge = (0,float('-inf'))
  for edge in faceEdges:
    edgeVec = getEdgeVector(mesh,edge)
    angle = angleBetweenVecAndPlane(edgeVec,planeNormal)
    if angle>alignedEdge[1]:
      alignedEdge = (edge,angle)
  return alignedEdge[0]

def angleBetweenVecAndPlane(vec,planeNormal):
  return math.asin(math.fabs(vec*planeNormal)/(vec.Length*planeNormal.Length))

def angleBetweenVectors(targetVec,vector):
  #RADIANS
  #return the angle variance of the vector from the target vector
  return Rhino.Geometry.Vector3d.VectorAngle(targetVec,vector)

def normalizeBuckleToEdgeLen(mesh,edgeIdx,buckleFactor):
  edgeLen = getEdgeLen(edgeIdx,mesh)
  return edgeLen*buckleFactor
  
def mapAngleToRange(angle):
  #angle is in range [0,pi], however is treated as [0,pi/2]
  #domain is a tuple: (lower,upper)
  normalDomain = (1,0)
  angleDomain = (0,math.pi/3.6) #NOTE: this range is tuned to spcific mesh!!!
  return (angle-normalDomain[0])*(normalDomain[1]-normalDomain[0])/(angleDomain[1]-angleDomain[0])+normalDomain[0]

def assignValuesToFaces(targetVec,mesh):
  '''
  ouput:
    values = dict, where: key = faceIdx, item = bucklingScore (0-1) for that face
  '''

  values = {}
  for i in range(mesh.Faces.Count):
    faceNormal = mesh.FaceNormals[i] 
    angle = angleBetweenVectors(targetVec,faceNormal)
    val = mapAngleToRange(angle) #maps to (0,1)
    if val<0:
      rs.AddSphere(mesh.Faces.GetFaceCenter(i),.3)
    values[i] = val
  return values

def getMesh(message=None):
  getter = Rhino.Input.Custom.GetObject()
  getter.SetCommandPrompt(message)
  getter.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh
  getter.SubObjectSelect = True
  getter.Get()
  if getter.CommandResult() != Rhino.Commands.Result.Success:
    return

  objref = getter.Object(0)
  obj = objref.Object()
  mesh = objref.Mesh()

  obj.Select(False)

  if obj:
    return mesh



if __name__=="__main__":
  viewFaceBuckles()


