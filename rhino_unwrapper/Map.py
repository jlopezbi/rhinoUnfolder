#Map
from rhino_helpers import getTVertsForEdge
class Map(object):
  """Map:a class for keeping track of the relation between the net and the mesh"""
  def __init__(self,mesh):
    #super(Map, self).__init__()
    self.meshVerts = {}
    self.meshEdges = {}
    self.meshFaces = {}
    for i in xrange(mesh.TopologyVertices.Count):
      self.meshVerts[i] = []
    for j in xrange(mesh.TopologyEdges.Count):
      self.meshEdges[j] = []
    #faces do not need to be lists, since each meshFace has one netFace

   # self.netToMesh = {} waittt this data can all be stored in the elements in net

  def updateEdgeMap(self,edge,netEdge):
    '''To be called imediately after adding an edge'''
    self.meshEdges[edge].append(netEdge)

  def updateVertMap(self,tVert,netVert):
    self.meshVerts[tVert].append(netVert)

  def getSiblingNetEdge(self,edge,netEdge):
    '''for a cut edge get the sibling edge'''
    edges = self.meshEdges[edge]
    netEdges = set(edges)
    netEdge = set([netEdge])
    singleEdge = netEdges-netEdge
    return singleEdge.pop()

  def getNetEdges(self,meshEdge):
    return self.meshEdges[meshEdge]

  def getRecentNetVertsForEdge(self,mesh,edge):
    meshI,meshJ = getTVertsForEdge(mesh,edge)
    netI = self.getRecentNetVert(meshI)
    netJ = self.getRecentNetVert(meshJ)
    return netI,netJ

  def getRecentNetVert(self,tVert):
    return self.meshVerts[tVert][-1] #get last item in list



