from rhino_helpers import *

def displayTVertIdx(mesh,vert,disp=None,color=(0,255,0,255)):
  if disp==None:
    disp = vert
  point = mesh.TopologyVertices.Item[vert]
  drawTextDot(point,str(disp),color)

def displayEdgeIdx(line,edgeIdx,color):
  cenX = (line.FromX+line.ToX)/2
  cenY = (line.FromY+line.ToY)/2
  cenZ = (line.FromZ+line.ToZ)/2
  point = Rhino.Geometry.Point3d(cenX,cenY,cenZ)
  return drawTextDot(point,str(edgeIdx),color)
  #rs.AddTextDot(eIdx,[cenX,cenY,cenZ])

def displayIJEdge(mesh,edgeIdx):
  vertI,vertJ = getTVerts(edgeIdx,mesh)
  pntI = mesh.TopologyVertices.Item[vertI]
  pntJ = mesh.TopologyVertices.Item[vertJ]
  rs.AddTextDot('I',pntI)
  rs.AddTextDot('J',pntJ)


def displayNormals(mesh):
  normLines = []
  for i in range(mesh.FaceNormals.Count):
    pntCenter = mesh.Faces.GetFaceCenter(i) #Point3d
    posVecCenter = Rhino.Geometry.Vector3d(pntCenter)
    vecNormal = mesh.FaceNormals.Item[i] #Vector3f
    vecNormal.Unitize()
    lineGuid = drawVector(vecNormal,pntCenter,(0,0,0,0))
    normLines.append(lineGuid)
  name = createGroup('Normals',normLines)
  return name


def displayVector(vector,position,color):
  endPnt = vec

def displayFaceIdxs(mesh):
  for i in xrange(mesh.Faces.Count):
    centerPnt = mesh.Faces.GetFaceCenter(i)
    rs.AddTextDot(str(i),centerPnt)

def displayFaceIdx(mesh,face):
  centerPnt = mesh.Faces.GetFaceCenter(face)
  rs.AddTextDot(str(face),centerPnt)

def displayMeshEdges(mesh,color,edgeIdxs,groupName):
  #TODO: try this: Rhino.Display.DisplayPipeline.DrawLine,  Rhino.Display.DisplayPipeline.DrawDottedLine  
  drawnEdges = {}
  if edgeIdxs:
    for edgeIdx in edgeIdxs:
      tVertI,tVertJ = getTVertsForEdge(mesh,edgeIdx)
      point3fI = mesh.TopologyVertices.Item[tVertI]
      point3fJ = mesh.TopologyVertices.Item[tVertJ]
      lineGuid,line = drawLine([point3fI,point3fJ],color,'None')
      drawnEdges[edgeIdx] = lineGuid

  #name = createGroup(groupName,drawnEdges)

  return drawnEdges


def setAttrColor(a,r,g,b):
  attr = Rhino.DocObjects.ObjectAttributes()
  attr.ObjectColor = System.Drawing.Color.FromArgb(a,r,g,b)
  attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
  return attr

def setAttrArrow(attr,strType):
  if strType == 'StartArrowhead':
    value =  Rhino.DocObjects.ObjectDecoration.StartArrowhead
  elif strType == 'EndArrowhead':
    value = Rhino.DocObjects.ObjectDecoration.EndArrowhead
  elif strType == 'BothArrowhead':
    value = Rhino.DocObjects.ObjectDecoration.BothArrowhead
  else:
    value = 0
  attr.ObjectDecoration = value
  return attr

def drawPolyline(polyline,color,arrowType):
  attr = setAttrColor(color[0],color[1],color[2],color[3])
  if arrowType:
    attr = setAttrArrow(attr,arrowType)
    
  poly_id = scriptcontext.doc.Objects.AddPolyline(polyline,attr)
  return poly_id,polyline

def drawVector(vector,startPnt,color,arrowType='EndArrowhead'):
  startPnt = Rhino.Geometry.Point3d(startPnt)
  endPnt = startPnt+vector 
  drawLine([startPnt,endPnt],color,arrowType)


def drawLine(points,color,arrowType,line=None):
  #points must be Point3d
  a,r,g,b = color
  if len(points)!=0:
    pntA,pntB = points
    line = Rhino.Geometry.Line(pntA,pntB)
  attr = setAttrColor(a,r,g,b)
  if arrowType:
    attr = setAttrArrow(attr,arrowType)

  # returns a Guid (globally unique identifier)
  lineGuid = scriptcontext.doc.Objects.AddLine(line,attr)
  return lineGuid,line

def translateLine(self,xForm):
  if self.line !=None:
    self.line.Transform(xForm)
    scriptcontext.doc.Objects.Replace(self.line_id,self.line)

def drawVector(vector,position,color):
  pntStart = Rhino.Geometry.Point3d(position)
  vecEnd = pntStart + vector
  pntEnd = Rhino.Geometry.Point3d(vecEnd)
  lineGuid = drawLine([pntStart,pntEnd],color,'EndArrowhead')
  return lineGuid

def drawTextDot(point,message,color):
  attrCol = setAttrColor(color[0],color[1],color[2],color[3])
  textDot = Rhino.Geometry.TextDot(message,point) #nust be point 3d
  return scriptcontext.doc.Objects.AddTextDot(textDot,attrCol)



''' Dispatch Table for drawing different types of FlatEdges '''
"""this is where specialized geometry like tabs might be added. 
Even though these functions seam redundant, keep this structure so that 
specialized draw commands for each type of edge is easier to implement

New thought: makes sense to have all edges displayed in addition to actual cad geom.
so basically draw all edges, (cut, fold, naked) and then have specialized functions for 
perforations, tabs, etc"""

def drawEdgeLine(flatEdge,color):
  p1,p2 = flatEdge.coordinates
  line = Rhino.Geometry.Line(p1,p2)
  lineGuid =  drawLine(line,flatEdge.edgeIdx,color,displayIdx=False)
  return lineGuid

'''
EDGE_DRAW_FUNCTIONS = {}

def drawFoldEdge(flatEdge):
  green = (0,49,224,61)
  lineGuid = drawLine(flatEdge.coordinates,green)
  return lineGuid
EDGE_DRAW_FUNCTIONS['fold'] = drawFoldEdge

def drawCutEdge(flatEdge):
  red = (0,237,43,120)
  lineGuid = drawLine(flatEdge.coordinates,red)
  return lineGuid
EDGE_DRAW_FUNCTIONS['cut'] = drawCutEdge

def drawNakedEdge(flatEdge):
  blue = (0,55,156,196)
  lineGuid = drawLine(flatEdge.coordinates,blue)
  return lineGuid
EDGE_DRAW_FUNCTIONS['naked'] = drawNakedEdge
'''

def drawNet(flatEdgePairs):
  '''
  flatEdgePairs is a list of lists which contain flatEdge objects
  flatEdge refers to an edge that is in the flattened net world
  '''
  net = []
  #flatten list
  flatEdges = [flatEdge for edgePair in flatEdgePairs for flatEdge in edgePair]
  for flatEdge in flatEdges:
    #flatEdge.clearAllGeom()
    lineGuid = EDGE_DRAW_FUNCTIONS[flatEdge.type](flatEdge)
    net.append(lineGuid)
    flatEdge.line_id = lineGuid

  netGroupName = createGroup("net",net)

  return netGroupName


#def drawNetAsMesh(flatEdgePairs)




