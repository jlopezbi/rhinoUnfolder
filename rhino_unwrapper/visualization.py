from rhino_helpers import *


def displayVector(vector, position, color):
    endPnt = vector

def setAttrColor(a, r, g, b):
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.ObjectColor = System.Drawing.Color.FromArgb(a, r, g, b)
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    return attr

def setAttrArrow(attr, strType):
    if strType == 'StartArrowhead':
        value = Rhino.DocObjects.ObjectDecoration.StartArrowhead
    elif strType == 'EndArrowhead':
        value = Rhino.DocObjects.ObjectDecoration.EndArrowhead
    elif strType == 'BothArrowhead':
        value = Rhino.DocObjects.ObjectDecoration.BothArrowhead
    else:
        value = 0
    attr.ObjectDecoration = value
    return attr

def drawPolyline(polyline, color, arrowType):
    attr = setAttrColor(color[0], color[1], color[2], color[3])
    if arrowType:
        attr = setAttrArrow(attr, arrowType)

    poly_id = scriptcontext.doc.Objects.AddPolyline(polyline, attr)
    return poly_id, polyline

def rhino_line(pntA,pntB):
    return Rhino.Geometry.Line(pntA,pntB)

def drawLine(points, color=(0,0,0,0), arrowType='None' ):
    # points must be Point3d
    if len(points) != 0:
        line = Rhino.Geometry.Line(points[0], points[1])
    attrCol = setAttrColor(color[0], color[1], color[2], color[3])
    if arrowType:
        attrCol = setAttrArrow(attrCol, arrowType)

    # returns a Guid (globally unique identifier)
    lineGuid = scriptcontext.doc.Objects.AddLine(line, attrCol)
    return lineGuid, line


def translateLine(self, xForm):
    if self.line is not None:
        self.line.Transform(xForm)
        scriptcontext.doc.Objects.Replace(self.line_id, self.line)


def drawVector(vector, position, color=[0,0,0,0]):
    pntStart = Rhino.Geometry.Point3d(position)
    vecEnd = position + vector
    pntEnd = Rhino.Geometry.Point3d(vecEnd)
    lineGuid = drawLine([pntStart, pntEnd], color, 'EndArrowhead')
    return lineGuid


def drawTextDot(point, message, color):
    attrCol = setAttrColor(color[0], color[1], color[2], color[3])
    textDot = Rhino.Geometry.TextDot(message, point)  # nust be point 3d
    return scriptcontext.doc.Objects.AddTextDot(textDot, attrCol)


''' Dispatch Table for drawing different types of FlatEdges '''
"""this is where specialized geometry like tabs might be added.
Even though these functions seam redundant, keep this structure so that
specialized draw commands for each type of edge is easier to implement

New thought: makes sense to have all edges displayed in addition to actual cad geom.
so basically draw all edges, (cut, fold, naked) and then have specialized functions for
perforations, tabs, etc"""


def drawEdgeLine(flatEdge, color):
    p1, p2 = flatEdge.coordinates
    line = Rhino.Geometry.Line(p1, p2)
    lineGuid = drawLine(line, flatEdge.edgeIdx, color, displayIdx=False)
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
    # flatten list
    flatEdges = [
        flatEdge for edgePair in flatEdgePairs for flatEdge in edgePair]
    for flatEdge in flatEdges:
        # flatEdge.clearAllGeom()
        lineGuid = EDGE_DRAW_FUNCTIONS[flatEdge.type](flatEdge)
        net.append(lineGuid)
        flatEdge.line_id = lineGuid

    netGroupName = createGroup("net", net)

    return netGroupName


# def drawNetAsMesh(flatEdgePairs)
