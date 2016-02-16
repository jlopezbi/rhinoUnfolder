from FlatGeom import FlatVert, FlatFace
import transformations as tf
import FlatEdge as fe
import Net as nt
import traversal as tr
from Map import Map
import rhinoscriptsyntax as rs
import Rhino

reload(tf)
reload(fe)
reload(nt)
reload(tr)


class UnFolder(object):
    """
    UnFolder is a class that generates a net
    from a mesh and a foldList
    """

    def __init__(self):
        # If this calss has no attributes need it be a class? Why not just a
        # bunch  of functions in a module?
        pass

    def initBasisInfo(self, mesh, origin):
        faceIdx = 0
        edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
        tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
        initBasisInfo = (faceIdx, edgeIdx, tVertIdx)
        return initBasisInfo

    def unfold(self, myMesh, userCuts, weightFunction, holeRadius=10):
        #### MAIN FUNCTION ####
        meshDual = tr.buildMeshGraph(myMesh, userCuts, weightFunction)
        foldList = tr.getSpanningKruskal(meshDual, myMesh.mesh)
        cutList = tr.getCutList(myMesh.mesh, foldList)

        origin = rs.WorldXYPlane()
        basisInfo = self.initBasisInfo(myMesh.mesh, origin)
        toBasis = origin

        net = nt.Net(myMesh, holeRadius)
        dataMap = Map(myMesh)
        net, dataMap = self.layoutFace(
            None, None, basisInfo, foldList, myMesh, toBasis, net, dataMap)
        return dataMap, net, foldList

    def layoutFace(self, fromFace, hopEdge, basisInfo,
                   foldList, myMesh, toBasis, net, dataMap):
        ''' Recursive Function to traverse through faces, hopping along fold edges
            input:
                depth = recursion level
                basisInfo = (faceIdx,edgeIdx,tVertIdx) information required to make basis
                foldList = list of edges that are folded
                myMesh = a wrapper for RhinoCommon mesh, to unfold
                toBasis = basis in flat world
            out/in:
                flatEdges = list containing flatEdges (a class that stores the edgeIdx,coordinates)
        '''
        xForm = tf.getTransform(basisInfo, toBasis, myMesh.mesh)
        netVerts, mapping = self.assignFlatVerts(
                myMesh, dataMap, net, hopEdge, basisInfo[0], xForm) #TODO: this method should probably belong to net
        net.flatFaces[basisInfo[0]] = FlatFace(netVerts, fromFace)

        faceEdges = myMesh.getFaceEdges(basisInfo[0])
        for edge in faceEdges:
            meshI, meshJ = myMesh.getTVertsForEdge(edge)
            netI = mapping[meshI]
            netJ = mapping[meshJ]
            #flatEdge = fe.FlatEdge(meshEdgeIdx=edge, vertAidx=netI,
                                   #vertBidx=netJ,fromFace=basisInfo[0]) # since faces have direct mapping this fromFace corresponds
            # to both the netFace and meshFace

            if edge in foldList:
                if not self.alreadyBeenPlaced(edge, dataMap.meshEdges):

                    newBasisInfo = self.getNewBasisInfo(basisInfo, edge, myMesh)
                    edgeCoords = (net.flatVerts[netI].point,net.flatVerts[netJ].point)

                    flatEdge = fe.FoldEdge(meshEdgeIdx=edge, vertAidx=netI,
                                   vertBidx=netJ,fromFace=basisInfo[0],toFace=newBasisInfo[0]) 
                    netEdge = net.addEdge(flatEdge)
                    dataMap.updateEdgeMap(edge, netEdge)

                    # RECURSE
                    recurse = True
                    newToBasis = tf.getBasisFlat(edgeCoords)
                    net, dataMap = self.layoutFace(
                        basisInfo[0], flatEdge, newBasisInfo, foldList, myMesh, newToBasis, net, dataMap)

            else:
                if len(dataMap.meshEdges[edge]) == 0:
                    flatEdge = fe.FlatEdge(meshEdgeIdx=edge, vertAidx=netI,
                                   vertBidx=netJ,fromFace=basisInfo[0])
                    netEdge = net.addEdge(flatEdge)
                    dataMap.updateEdgeMap(edge, netEdge)

                elif len(dataMap.meshEdges[edge]) == 1:
                    otherEdge = dataMap.meshEdges[edge][0]
                    otherFace = myMesh.getOtherFaceIdx(edge,basisInfo[0])
                    flatEdge = fe.CutEdge(meshEdgeIdx=edge,
                                          vertAidx=netI,
                                          vertBidx=netJ,
                                          fromFace=basisInfo[0],
                                          toFace=otherFace,
                                          sibling=otherEdge)
                    flatEdge.get_other_face_center(myMesh, basisInfo[0], xForm)
                    netEdge = net.addEdge(flatEdge)
                    dataMap.updateEdgeMap(edge, netEdge)
                    sibFlatEdge = net.flatEdges[otherEdge]
                    net.flatEdges[otherEdge] = fe.change_to_cut_edge(sibFlatEdge,netEdge)
        return net, dataMap

    def assignFlatVerts(self, mesh, dataMap, net, hopEdge, face, xForm):
        '''
        add valid flatVerts to flatVerts list and also return
        a list of netVerts
        '''

        faceTVerts = mesh.getTVertsForFace(face)
        netVerts = []
        hopMeshVerts = []
        mapping = {}

        if hopEdge is not None:
            netI, netJ = [hopEdge.vertAidx, hopEdge.vertAidx]
            hopMeshVerts = [
                net.flatVerts[netI].tVertIdx,
                net.flatVerts[netJ].tVertIdx]
            mapping[hopMeshVerts[0]] = netI
            mapping[hopMeshVerts[1]] = netJ

        seen = []
        for tVert in faceTVerts:
            if tVert not in seen:  # avoid duplicates (triangle faces)
                seen.append(tVert)
                if tVert not in hopMeshVerts:
                    point = self.transformPoint(mesh.mesh, tVert, xForm)
                    flatVert = FlatVert(tVert, point)
                    netVert = net.addVert(flatVert)
                    dataMap.meshVerts[tVert].append(netVert)
                    netVerts.append(netVert)
                    mapping[tVert] = netVert
                else:
                    # this section is important for preserving order
                    if tVert == net.flatVerts[netI].tVertIdx:
                        netVerts.append(netI)
                    elif tVert == net.flatVerts[netJ].tVertIdx:
                        netVerts.append(netJ)
                    pass
        return netVerts, mapping

    def getNetEdges(self, mesh, edge, netVerts, dataMap):
        I, J = mesh.getTVertsForEdge(edge)
        vertI = dataMap.get

    def transformPoint(self, mesh, tVert, xForm):
        point = Rhino.Geometry.Point3d(mesh.TopologyVertices.Item[tVert])
        point.Transform(xForm)
        point.Z = 0.0  # TODO: find where error comes from!!! (rounding?)
        return point

    def alreadyBeenPlaced(self, edge, meshEdges):
        return len(meshEdges[edge]) > 0

    def getNewBasisInfo(self, oldBasisInfo, testEdgeIdx, myMesh):
        faceIdx, edgeIdx, tVertIdx = oldBasisInfo
        newFaceIdx = myMesh.getOtherFaceIdx(testEdgeIdx, faceIdx)
        newEdgeIdx = testEdgeIdx
        newTVertIdx = myMesh.mesh.TopologyEdges.GetTopologyVertices(
            testEdgeIdx).I  # convention: useI
        return newFaceIdx, newEdgeIdx, newTVertIdx

