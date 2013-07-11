import Rhino
import scriptcontext
import System.Drawing
from rhino_helpers import *

def setAttrColor(a,r,g,b):
  attr = Rhino.DocObjects.ObjectAttributes()
  attr.ObjectColor = System.Drawing.Color.FromArgb(a,r,g,b)
  attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
  return attr

def displayEdgeIdx(line,edgeIdx):
  cenX = (line.FromX+line.ToX)/2
  cenY = (line.FromY+line.ToY)/2
  cenZ = (line.FromZ+line.ToZ)/2
  eIdx = str(edgeIdx)
  rs.AddTextDot(eIdx,[cenX,cenY,cenZ])

def displayNormals(mesh):
  normLines = []
  for i in range(mesh.FaceNormals.Count):
    p1 = mesh.Faces.GetFaceCenter(i)
    p2 = p1 + mesh.FaceNormals.Item[i]
    normLines.append(rs.AddLine(p1,p2))
  createGroup("normLines",normLines)

def displayFaceIdxs(mesh):
  for i in xrange(mesh.Faces.Count):
    centerPnt = mesh.Faces.GetFaceCenter(i)
    rs.AddTextDot(str(i),centerPnt)

def displayMeshCutEdges(mesh,foldList):
  seamRed = (0,255,0,0) 
  for i in range(mesh.TopologyEdges.Count):
    if i not in foldList:
      tVertI,tVertJ = getTVerts(i,mesh)
      point3fI = mesh.TopologyVertices.Item[tVertI]
      point3fJ = mesh.TopologyVertices.Item[tVertJ]
      line = Rhino.Geometry.Line(point3fI,point3fJ)
      edgeLine = drawLine(line,i,seamRed,displayIdx=False)

def displayMeshEdges(mesh,color,edgeIdxs):
  "generalized mesh edge display: replace this with above later"
  if edgeIdxs:
    for edgeIdx in edgeIdxs:
      tVertI,tVertJ = getTVerts(edgeIdx,mesh)
      point3fI = mesh.TopologyVertices.Item[tVertI]
      point3fJ = mesh.TopologyVertices.Item[tVertJ]
      line = Rhino.Geometry.Line(point3fI,point3fJ)
      edgeLine = drawLine(line,edgeIdx,color,displayIdx=False)


def drawLine(line,edgeIdx,color,displayIdx=False):
  # if isFoldEdge:
  #   #GREEN for foldEdge
  #   attrCol = setAttrColor(0,49,224,61)
  # else:
  #   #RED for cutEdge
  #   attrCol = setAttrColor(0,237,43,120)

  attrCol = setAttrColor(color[0],color[1],color[2],color[3])

  if displayIdx:
    displayEdgeIdx(line,edgeIdx)

  return scriptcontext.doc.Objects.AddLine(line,attrCol)



''' Dispatch Table for drawing different types of FlatEdges '''
EDGE_DRAW_FUNCTIONS = {}

def drawFoldEdge(flatEdge):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  green = (0,49,224,61)
  return drawLine(line,flatEdge.edgeIdx,green,displayIdx=False)
EDGE_DRAW_FUNCTIONS['fold'] = drawFoldEdge

def drawCutEdge(flatEdge):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  red = (0,237,43,120)
  return drawLine(line,flatEdge.edgeIdx,red,displayIdx=False)
EDGE_DRAW_FUNCTIONS['cut'] = drawCutEdge

def drawNakedEdge(flatEdge):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  blue = (0,55,156,196)
  return drawLine(line,flatEdge.edgeIdx,blue,displayIdx=False)
EDGE_DRAW_FUNCTIONS['naked'] = drawNakedEdge

def drawNet(flatEdgePairs):
  net = []
  flatEdges = [flatEdge for edgePair in flatEdgePairs for flatEdge in edgePair]
  for flatEdge in flatEdges:
    net.append(EDGE_DRAW_FUNCTIONS[flatEdge.type](flatEdge))
  createGroup("net",net)
