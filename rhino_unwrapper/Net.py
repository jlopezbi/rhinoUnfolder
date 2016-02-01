import segmentation as sg
from rhino_helpers import createGroup, getEdgesForVert
from FlatGeom import FlatVert
import FlatEdge as fe
import Rhino
import rhinoscriptsyntax as rs
import math

reload(sg)
reload(fe)


class Net():
    """ What does a net do?, slash know about?
        => it stores the mesh that is the net. In fact perhaps should just use rhino's mesh! but lets save that for later
    Right now the net does this:
        * Segmentation
            * Selection
        * Display
    """

    def __init__(self, mesh, holeRadius):
        self.holeRadius = holeRadius
        self.flatVerts = []
        self.flatEdges = []
        self.flatFaces = [None] * mesh.Faces.Count
        self.angleThresh = math.radians(3.3)
        self.mesh = mesh

        #self.groups,self.leaders = segmentIsland(self.flatFaces,[])

    def addEdge(self, flatEdge):
        self.flatEdges.append(flatEdge)
        return len(self.flatEdges) - 1

    def addVert(self, flatVert):
        self.flatVerts.append(flatVert)
        return len(self.flatVerts) - 1

    '''SEGMENTATION'''

    def findInitalSegments(self):
        group, leader = sg.segmentIsland(self.flatFaces, [])
        self.groups = group
        self.leaders = leader

    def findSegment(self, flatEdgeCut, face):
        assert(flatEdgeCut.type == 'fold')
        island = self.getGroupForMember(face)
        self.removeFaceConnection(flatEdgeCut)
        group, leader = sg.segmentIsland(self.flatFaces, island)
        self.updateIslands(group, leader, face)
        return group[leader[face]]

    def copyAndReasign(self, mesh, dataMap, flatEdgeCut, idx, segment, face):
        flatEdgeCut.type = 'cut'
        flatEdgeCut.resetFromFace(face)
        changedVertPairs = self.makeNewNetVerts(dataMap, flatEdgeCut)
        newEdge = self.makeNewEdge(
            dataMap,
            changedVertPairs,
            flatEdgeCut.edgeIdx,
            idx,
            face)
        flatEdgeCut.pair = newEdge
        flatEdgeCut.hasTab = True
        flatEdgeCut.drawEdgeLine(self.flatVerts, self.angleThresh, self.mesh)
        # flatEdgeCut.drawHoles(self,connectorDist,safetyRadius,holeRadius)
        self.resetSegment(mesh, dataMap, changedVertPairs, segment)

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

                netEdge.drawEdgeLine(self.flatVerts,self.angleThresh,self.mesh)
                #rs.AddObjectsToGroup(geom, group)


                # if netEdge.type=='cut':
                #   #TODO: perhaps user input for hole parameters?
                #   netEdge.drawHoles(self,.1,.08,.07)
        return collection

    def redrawSegment(self, translatedEdges):
        group = rs.AddGroup()
        geom = []
        for netEdge in translatedEdges:
            geom.append(self.drawEdge(netEdge))
        grouped = rs.AddObjectsToGroup(geom, group)
        if grouped is None:
            print "failed to make segment group"
        else:
            print "made segment group of" + str(grouped) + " elements"

    def removeFaceConnection(self, flatEdgeCut):
        faceA = flatEdgeCut.fromFace
        faceB = flatEdgeCut.toFace
        netFaceA = self.flatFaces[faceA]
        netFaceB = self.flatFaces[faceB]
        if netFaceB.fromFace == faceA:
            netFaceB.fromFace = None
        elif netFaceA.fromFace == faceB:
            netFaceA.fromFace = None

    def makeNewEdge(self, dataMap, changedVertPairs, meshEdge, idx, face):
        newVertI = changedVertPairs[0][0]
        newVertJ = changedVertPairs[1][0]
        newFlatEdge = fe.FlatEdge(meshEdge, newVertI, newVertJ)
        newFlatEdge.fromFace = face
        newFlatEdge.type = 'cut'
        newFlatEdge.hasTab = True
        newFlatEdge.pair = idx
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

    def resetSegment(self, mesh, dataMap, changedVertPairs, segment):
        self.resetFaces(changedVertPairs, segment)
        self.resetEdges(mesh, dataMap, changedVertPairs, segment)

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

    def resetEdges(self, mesh, dataMap, changedVertPairs, segment):
        '''
        reset all edges touching the newely added vertices
        '''
        # REPLACE: if using he-mesh then this will be unnecessary
        for pair in changedVertPairs:
            newVert, oldVert = pair
            tVert = self.flatVerts[newVert].tVertIdx
            # in original mesh,eventually use he-mesh
            edges = getEdgesForVert(mesh, tVert)
            for edge in edges:
                netEdges = dataMap.getNetEdges(edge)
                for netEdge in netEdges:
                    flatEdge = self.getFlatEdge(netEdge)
                    netPair = flatEdge.getNetVerts()
                    if oldVert in netPair and flatEdge.fromFace in segment:
                        #assert(flatEdge.fromFace in segment), "flatEdge not in segment"
                        flatEdge.reset(oldVert, newVert)

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

    '''SELECTION'''

    def getFlatEdgeForLine(self, value):
        # assert guid?
        for i, flatEdge in enumerate(self.flatEdges):
            if flatEdge.line_id == value:
                return flatEdge, i
        return

    def getFlatEdge(self, netEdge):
        return self.flatEdges[netEdge]

    '''DRAWING'''
    """
  I think flatEdges should know how to drawthemselves! not the net!
  """

    def drawEdges_simple(self):
        for netEdge in self.flatEdges:
            netEdge.drawEdgeLine(self.flatVerts, self.angleThresh, self.mesh)





    def _drawEdge(self, netEdge):
        # DEPRICATE! thus the _
        collection = []
        collection.append(
            netEdge.drawEdgeLine(
                self.flatVerts,
                self.angleThresh,
                self.mesh))
        if netEdge.type == 'cut':
            collection.append(netEdge.drawTab(self))
            if netEdge.hasTab:
                pass
               # collection.append(netEdge.drawTab(self))
            else:
                collection.append(netEdge.drawFaceHole(self, self.holeRadius))
        return collection

    def drawEdges(self, netGroupName):
        collection = []
        for netEdge in self.flatEdges:

            # if netEdge.type=='cut':
            # netEdge.drawHoles(self,connectorDist,safetyRadius,holeRadius)

            subCollection = self.drawEdge(netEdge)
            for item in subCollection:
                collection.append(item)
        createGroup(netGroupName, collection)

    def drawFaces(self, netGroupName):
        collection = []
        for face in self.flatFaces:
            collection.append(face.draw(self.flatVerts))
        createGroup(netGroupName, collection)
