import Rhino
import scriptcontext
import System.Drawing

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

def drawLine(line,edgeIdx,isFoldEdge,displayIdx):
  if isFoldEdge:
    #GREEN for foldEdge
    attrCol = setAttrColor(0,49,224,61)
  else:
    #RED for cutEdge
    attrCol = setAttrColor(0,237,43,120)

  scriptcontext.doc.Objects.AddLine(line,attrCol)

  if displayIdx:
    displayEdgeIdx(line,edgeIdx)



''' Dispatch Table for drawing different types of FlatEdges '''
EDGE_DRAW_FUNCTIONS = {}

def drawFoldEdge(flatEdge):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  drawLine(line,flatEdge.edgeIdx,isFoldEdge=True,displayIdx=False)
EDGE_DRAW_FUNCTIONS['fold'] = drawFoldEdge

def drawCutEdge(flatEdge):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  drawLine(line,flatEdge.edgeIdx,isFoldEdge=False,displayIdx=False)
EDGE_DRAW_FUNCTIONS['cut'] = drawCutEdge


def drawNet(flatEdgePairs):
  flatEdges = [flatEdge for edgePair in flatEdgePairs for flatEdge in edgePair]
  for flatEdge in flatEdges:
    EDGE_DRAW_FUNCTIONS[flatEdge.type]()
