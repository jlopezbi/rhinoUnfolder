from rhino_helpers import *



def displayEdgeIdx(line,edgeIdx,color):
  cenX = (line.FromX+line.ToX)/2
  cenY = (line.FromY+line.ToY)/2
  cenZ = (line.FromZ+line.ToZ)/2
  point = Rhino.Geometry.Point3d(cenX,cenY,cenZ)
  return drawTextDot(point,str(edgeIdx),color)
  #rs.AddTextDot(eIdx,[cenX,cenY,cenZ])



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


def displayMeshEdges(mesh,color,edgeIdxs,groupName):
  drawnEdges = []
  if edgeIdxs:
    for edgeIdx in edgeIdxs:
      tVertI,tVertJ = getTVerts(edgeIdx,mesh)
      point3fI = mesh.TopologyVertices.Item[tVertI]
      point3fJ = mesh.TopologyVertices.Item[tVertJ]
      line = Rhino.Geometry.Line(point3fI,point3fJ)
      edgeLine = drawLine(line,edgeIdx,color,displayIdx=False)
      drawnEdges.append(edgeLine)

  name = createGroup(groupName,drawnEdges)

  return name


def setAttrColor(a,r,g,b):
  attr = Rhino.DocObjects.ObjectAttributes()
  attr.ObjectColor = System.Drawing.Color.FromArgb(a,r,g,b)
  attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
  return attr


def drawLine(line,edgeIdx,color,displayIdx=False):

  attrCol = setAttrColor(color[0],color[1],color[2],color[3])

  if displayIdx:
    displayEdgeIdx(line,edgeIdx)
  # returns a Guid (globally unique identifier)
  return scriptcontext.doc.Objects.AddLine(line,attrCol)

def drawTextDot(point,message,color):
  attrCol = setAttrColor(color[0],color[1],color[2],color[3])
  textDot = Rhino.Geometry.TextDot(message,point) #nust be point 3d
  return scriptcontext.doc.Objects.AddTextDot(textDot,attrCol)



''' Dispatch Table for drawing different types of FlatEdges '''
"""this is where specialized geometry like tabs might be added. 
Even though these functions seam redundant, keep this structure so that 
specialized draw commands for each type of edge is easier to implement"""

EDGE_DRAW_FUNCTIONS = {}

def drawFoldEdge(flatEdge):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  green = (0,49,224,61)
  geom =  drawLine(line,flatEdge.edgeIdx,green,displayIdx=False)
  flatEdge.geom = geom
  return geom
EDGE_DRAW_FUNCTIONS['fold'] = drawFoldEdge

def drawCutEdge(flatEdge):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  red = (0,237,43,120)
  geom = drawLine(line,flatEdge.edgeIdx,red,displayIdx=False)
  flatEdge.geom = geom
  return geom
EDGE_DRAW_FUNCTIONS['cut'] = drawCutEdge

def drawNakedEdge(flatEdge):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  blue = (0,55,156,196)
  geom = drawLine(line,flatEdge.edgeIdx,blue,displayIdx=False)
  flatEdge.geom = geom
  return geom
EDGE_DRAW_FUNCTIONS['naked'] = drawNakedEdge

def drawNet(flatEdgePairs):
  '''
  flatEdgePairs is a list of lists which contain flatEdge objects
  flatEdge refers to an edge that is in the flattened net world
  '''
  net = []
  #flatten list
  flatEdges = [flatEdge for edgePair in flatEdgePairs for flatEdge in edgePair]
  for flatEdge in flatEdges:
    net.append(EDGE_DRAW_FUNCTIONS[flatEdge.type](flatEdge))
  netGroupName = createGroup("net",net)

  return netGroupName

#def drawNetAsMesh(flatEdgePairs)




