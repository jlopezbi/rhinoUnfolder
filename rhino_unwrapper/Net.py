import segmentation as sg
from rhino_helpers import createGroup 
from flatGeom import FlatVert
import flatGeom
import flatEdge as fe
import Rhino
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs
import math

reload(flatGeom)
reload(sg)
reload(fe)


class Net():
    """ 
    What if Net was composed of islands?! each island has verts,edge and faces.
    What does a net do?, slash know about?
        => it stores the mesh that is the net. In fact perhaps should just use rhino's mesh! but lets save that for later
    Right now the net does this:
        * Segmentation <= this is the main thing!
            * Selection
        * Display

    Queries: (this will help determine best Data structure)
        * for a given edge its parent face and its otherParnet face (assuming a manifold edge)
        * for a given cut edge, its corresponding edge
        * for a given edge, the two sets of edges/faces/verts on either side, or for a given edge, the set of edges/faces/verts on the side indicated by the user (faster)
        non essential:
        * for a given edge, the corrseponding edge in the 3d mesh
    """
#myMesh.mesh.Faces.Count

    def __init__(self, myMesh, holeRadius=10):
        self.holeRadius = holeRadius
        self.angleThresh = math.radians(3.3)
        self.myMesh = myMesh
        self.islands = []
        #self.groups,self.leaders = segmentIsland(self.flatFaces,[])

    def add_island(self,island):
        self.islands.append(island)

    '''SEGMENTATION, seems like should be a seperate thing!'''

    def findInitalSegments(self):
        group, leader = sg.segmentIsland(self.flatFaces, [])
        self.groups = group
        self.leaders = leader

    def findSegment(self, flatEdgeCut, face):
        island = self.getGroupForMember(face)
        self.removeFaceConnection(flatEdgeCut)
        group, leader = sg.segmentIsland(self.flatFaces, island)
        self.updateIslands(group, leader, face)
        return group[leader[face]]

    def getGroupForMember(self, member):
        if member not in self.leaders.keys():
            print "face not in leaders: ",
            print member
            return
        leader = self.leaders[member]
        return self.groups[leader]

    def updateIslands(self, newGroups, newLeaders, face):
        # get rid of old island
        leader = self.leaders[face]
        del self.groups[leader]

        for group in newGroups.items():
            self.groups[group[0]] = group[1]
        for leader in newLeaders.items():
            self.leaders[leader[0]] = leader[1]

    def copyAndReasign(self, dataMap, flatEdge, idx, segment, face):
        # TODO: this must change because of change to cut/fold edge types
        # GOT TO REWORK THIS ONE
        newEdgeIdx = len(self.flatEdges)
        resetEdge = fe.change_to_cut_edge(flatEdge,newEdgeIdx)
        resetEdge.resetFromFace(face)
        changedVertPairs = self.makeNewNetVerts(dataMap, flatEdge)
        newEdge = self.makeNewEdge(
            dataMap,
            changedVertPairs,
            flatEdge.meshEdgeIdx,
            idx,
            face,flatEdge.getOtherFace(face))
        flatEdge.pair = newEdge
        flatEdge.show_line(self.flatVerts)
        # flatEdge.drawHoles(self,connectorDist,safetyRadius,holeRadius)
        self.resetSegment(dataMap, changedVertPairs, segment)

    def translateSegment(self, segment, xForm):
        # TODO: make a more efficent version of this, would be easier if half-edge or
        # winged edge mesh. H-E: could traverse edges recursively, first going to sibling h-edge
        # Sstopping when the edge points to no other edge(naked),or to a face not in the segment,or
        # if the h-edge is part of the user-selected edge to be cut
        group = rs.AddGroup()
        collection = []
        movedNetVerts = []
        for netEdge in self.flatEdges:
            if netEdge.fromFace in segment:
                collection.append(netEdge)
                netEdge.clearAllGeom()
                netEdge.translateGeom(movedNetVerts, self.flatVerts, xForm)
        return collection

    def redrawSegment(self, translatedEdges):
        geom = []
        for netEdge in translatedEdges:
            netEdge.show_line(self.flatVerts)

    def removeFaceConnection(self, flatEdgeCut):
        faceA = flatEdgeCut.fromFace
        faceB = flatEdgeCut.toFace
        netFaceA = self.flatFaces[faceA]
        netFaceB = self.flatFaces[faceB]
        if netFaceB.fromFace == faceA:
            netFaceB.fromFace = None
        elif netFaceA.fromFace == faceB:
            netFaceA.fromFace = None

    def makeNewEdge(self, dataMap, changedVertPairs, meshEdge, otherEdge,
    fromFace,toFace):
        newVertI = changedVertPairs[0][0]
        newVertJ = changedVertPairs[1][0]
        newFlatEdge = fe.CutEdge(meshEdgeIdx=meshEdge,
                                 vertAidx=newVertI,
                                 vertBidx=newVertJ,
                                 fromFace=fromFace,
                                 toFace=toFace,
                                 sibling=otherEdge)
        newFlatEdge.hasTab = True
        newFlatEdge.tabFaceCenter = self.flatFaces[toFace].getCenterPoint(self.flatVerts)
        
# This is where need to add a tabFaceCenter thing that will find the otherFace
        # of the edge and find its center
        # TODO: need to set tab angles or something. NOTE: .fromFace and
        # .toFace of flatEdge referes to a MESH face!!
        netEdge = self.addEdge(newFlatEdge)
        dataMap.updateEdgeMap(meshEdge, netEdge)
        return netEdge

    def makeNewNetVerts(self, dataMap, flatEdgeCut):
        oldNetI, oldNetJ = flatEdgeCut.getNetVerts()
        flatI, flatJ = flatEdgeCut.getFlatVerts(self.flatVerts)
        pointI = Rhino.Geometry.Point3d(flatI.point)  # important copy vert
        pointJ = Rhino.Geometry.Point3d(flatJ.point)
        newI = FlatVert(flatI.tVertIdx, pointI)
        newJ = FlatVert(flatJ.tVertIdx, pointJ)
        newNetI = self.addVert(newI)
        newNetJ = self.addVert(newJ)
        dataMap.updateVertMap(flatI.tVertIdx, newNetI)
        dataMap.updateVertMap(flatJ.tVertIdx, newNetJ)
        return [(newNetI, oldNetI), (newNetJ, oldNetJ)]

    def resetSegment(self, dataMap, changedVertPairs, segment):
        self.resetFaces(changedVertPairs, segment)
        self.resetEdges(dataMap, changedVertPairs, segment)

    def resetFaces(self, changedVertPairs, segment):
        # REPLACE: this is slow hack
        newVertI, oldVertI = changedVertPairs[0]
        newVertJ, oldVertJ = changedVertPairs[1]
        for face in segment:
            verts = self.flatFaces[face].vertices
            if oldVertI in verts:
                index = verts.index(oldVertI)
                verts.insert(index, newVertI)  # does order matter? yes
                verts.pop(index + 1)
            if oldVertJ in verts:
                index = verts.index(oldVertJ)
                verts.insert(index, newVertJ)  # does order matter? yes
                verts.pop(index + 1)

    def resetEdges(self, dataMap, changedVertPairs, segment):
        '''
        reset all edges touching the newely added vertices
        '''
        # REPLACE: if using he-mesh then this will be unnecessary
        for pair in changedVertPairs:
            newVert, oldVert = pair
            tVert = self.flatVerts[newVert].tVertIdx
            print "Tvert:",
            print tVert
            # in original mesh,eventually use he-mesh
            edges = self.myMesh.getEdgesForVert(tVert)
            for edge in edges:
                netEdges = dataMap.getNetEdges(edge)
                for netEdge in netEdges:
                    flatEdge = self.getFlatEdge(netEdge)
                    netPair = flatEdge.getNetVerts()
                    if oldVert in netPair and flatEdge.fromFace in segment:
                        #assert(flatEdge.fromFace in segment), "flatEdge not in segment"
                        flatEdge.reset(oldVert, newVert)


class Island(object):

    def __init__(self):
        self.flatVerts = []
        self.flatEdges = []
        self.flatFaces = []  

    def add_face(self,flatFace):
        self.flatFaces.append(flatFace)
        return len(self.flatFaces) - 1
    
    def add_face_from_verts(self,*args):
        '''any number of ordered vertex indices '''
        flatFace = flatGeom.FlatFace(args)
        return self.add_face(flatFace)

    def add_edge(self, flatEdge):
        self.flatEdges.append(flatEdge)
        return len(self.flatEdges) - 1

    def add_edge_from_verts(self,vertA,vertB):
        return self.add_edge(fe.FlatEdge(vertAidx=vertA,vertBidx=vertB))

    def add_vert_from_points(self,x,y,z):
        return self.add_vert(flatGeom.FlatVert.from_coordinates(x,y,z))

    def add_vert(self, flatVert):
        self.flatVerts.append(flatVert)
        return len(self.flatVerts) - 1

    def draw_verts(self):
        for vert in self.flatVerts:
            vert.display()

    def draw_edges(self):
        for netEdge in self.flatEdges:
            netEdge.show_line(self.flatVerts)

    def draw_faces(self, netGroupName=''):
        collection = []
        for face in self.flatFaces:
            collection.append(face.draw(self.flatVerts))
        createGroup(netGroupName, collection)

    def getFlatEdgeForLine(self, value):
        # assert guid?
        for i, flatEdge in enumerate(self.flatEdges):
            if flatEdge.line_id == value:
                return flatEdge, i
        return

    def getFlatEdge(self, netEdge):
        return self.flatEdges[netEdge]

