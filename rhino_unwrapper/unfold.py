from FlatGeom import FlatVert, FlatFace
import transformations as tf
import FlatEdge as fe
import Net as nt
import traversal as tr
import Map
import mesh
import rhino_inputs as ri
import weight_functions as wf

import rhinoscriptsyntax as rs
import Rhino
import collections,inspect

reload(tf)
reload(fe)
reload(nt)
reload(tr)

def all_weight_functions():
    return dict([m for m in inspect.getmembers(wf, inspect.isfunction)])

class UnFolder(object):
    """
    UnFolder is a class that unfolds a mesh by creating a net
    THIS IS THE NEW MAIN PLACE IN THE CODE!
    """

    def __init__(self):
        self.myMesh  = mesh.Mesh(ri.getMesh("select mesh to unfold"))
        self.dataMap = Map.Map(self.myMesh)
        if not self.myMesh: return
        self.user_cuts = ri.getUserCuts(self.myMesh)
        if not self.user_cuts: return
        self.weightFunction = ri.getOptions_dict(all_weight_functions())
        if not self.weightFunction: return
        self.dual = tr.buildMeshGraph(self.myMesh,
                                      self.user_cuts,
                                      self.weightFunction)
        self.fold_list = tr.getSpanningKruskal(self.dual, self.myMesh.mesh)
        self.cut_list = tr.getCutList(self.myMesh.mesh, self.fold_list)
        self.net = nt.Net(self.myMesh)
        self.islandCreator = IslandCreator(self.dataMap, self.myMesh)

    def initBasisInfo(self, mesh, origin):
        faceIdx = 0
        edgeIdx = mesh.TopologyEdges.GetEdgesForFace(faceIdx).GetValue(0)
        tVertIdx = mesh.TopologyEdges.GetTopologyVertices(edgeIdx).I
        initBasisInfo = Basis(faceIdx, edgeIdx, tVertIdx)
        return initBasisInfo
    
    def make_origin_basis(self):
        origin = rs.WorldXYPlane()
        return Basis(origin[0],origin[1],origin[2])

    def unfold(self):
        fromBasis = self.initBasisInfo(self.myMesh.mesh, origin)
        toBasis = self.make_origin_basis() 

        # currently assumes one island makes up net
        island = self.islandCreator.make_island(self.fold_list,fromBasis,toBasis)
        self.net.add_island(island)

if __name__ == "__main__":
    unfolder = UnFolder()
    unfolder.unfold()


MeshFrame = collections.namedtuple('MeshFrame',['face','edge','tVert'])
#Island = collections.nametuple('Island',['flatVerts','flatEdges','flatFaces'])

class IslandCreator(object):
    """
    traverses a mesh to create an island
    """
    def __init__(self,dataMap=None,myMesh=None):
        self.island = nt.Island()
        self.dataMap = dataMap
        self.myMesh = myMesh

    def make_island(self,foldList,face,toBasis):
        self.foldList = foldList
        self.layout_face(None,None,fromBasis,toBasis)

    def layout_face(self, fromFace, hopEdge, meshFrame, toBasis):
        ''' Recursive Function to traverse through faces, hopping along fold edges
            input:
                depth = recursion level
                meshFrame = (faceIdx,edgeIdx,tVertIdx) information required to make basis
                self.myMesh = a wrapper for RhinoCommon mesh, to unfold
                toBasis = basis in flat world
            out/in:
                flatEdges = list containing flatEdges (a class that stores the edgeIdx,coordinates)
        '''
        mesh_frame = tf.getBasisOnMesh(meshFrame,self.myMesh.mesh)
        xForm = tf.createTransformMatrix(mesh_frame, toBasis)
        netVerts, mapping = self.assignFlatVerts(self.myMesh, self.dataMap, hopEdge,
                                                 meshFrame.face, xForm) 
        self.island.flatFaces[meshFrame.face] = FlatFace(netVerts, fromFace)

        faceEdges = self.myMesh.getFaceEdges(meshFrame.face)
        for edge in faceEdges:
            meshI, meshJ = self.myMesh.getTVertsForEdge(edge)
            netI = mapping[meshI]
            netJ = mapping[meshJ]
            #flatEdge = fe.FlatEdge(meshEdgeIdx=edge, vertAidx=netI,
                                   #vertBidx=netJ,fromFace=meshFrame[0]) # since faces have direct mapping this fromFace corresponds
            # to both the netFace and meshFace

            if edge in self.foldList:
                if not self.alreadyBeenPlaced(edge, self.dataMap.meshEdges):

                    new_mesh_frame = self.getNewBasisInfo(meshFrame, edge, self.myMesh)
                    edgeCoords = (self.island.flatVerts[netI].point,self.island.flatVerts[netJ].point)

                    flatEdge = fe.FoldEdge(meshEdgeIdx=edge, vertAidx=netI,
                                   vertBidx=netJ,fromFace=meshFrame.face,toFace=new_mesh_frame.face) 
                    netEdge = self.island.addEdge(flatEdge)
                    self.dataMap.updateEdgeMap(edge, netEdge)

                    # RECURSE
                    recurse = True
                    new_net_frame = tf.get_net_frame(edgeCoords)
                    self.dataMap = self.layout_face( meshFrame.face, flatEdge, new_mesh_frame,new_net_frame)

            else:
                if len(self.dataMap.meshEdges[edge]) == 0:
                    flatEdge = fe.FlatEdge(meshEdgeIdx=edge, vertAidx=netI,
                                   vertBidx=netJ,fromFace=meshFrame.face)
                    netEdge = self.island.addEdge(flatEdge)
                    self.dataMap.updateEdgeMap(edge, netEdge)

                elif len(self.dataMap.meshEdges[edge]) == 1:
                    otherEdge = self.dataMap.meshEdges[edge][0]
                    otherFace = self.myMesh.getOtherFaceIdx(edge,meshFrame.face)
                    flatEdge = fe.CutEdge(meshEdgeIdx=edge,
                                          vertAidx=netI,
                                          vertBidx=netJ,
                                          fromFace=meshFrame.face,
                                          toFace=otherFace,
                                          sibling=otherEdge)
                    flatEdge.get_other_face_center(self.myMesh, meshFrame.face, xForm)
                    netEdge = self.island.addEdge(flatEdge)
                    self.dataMap.updateEdgeMap(edge, netEdge)
                    sibFlatEdge = self.island.flatEdges[otherEdge]
                    self.island.flatEdges[otherEdge] = fe.change_to_cut_edge(sibFlatEdge,netEdge)

    def assignFlatVerts(self, mesh, dataMap,  hopEdge, face, xForm):
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
                self.island.flatVerts[netI].tVertIdx,
                self.island.flatVerts[netJ].tVertIdx]
            mapping[hopMeshVerts[0]] = netI
            mapping[hopMeshVerts[1]] = netJ

        seen = []
        for tVert in faceTVerts:
            if tVert not in seen:  # avoid duplicates (triangle faces)
                seen.append(tVert)
                if tVert not in hopMeshVerts:
                    point = self.transformPoint(mesh.mesh, tVert, xForm)
                    flatVert = FlatVert(tVert, point)
                    netVert = self.island.addVert(flatVert)
                    dataMap.meshVerts[tVert].append(netVert)
                    netVerts.append(netVert)
                    mapping[tVert] = netVert
                else:
                    # this section is important for preserving order
                    if tVert == self.island.flatVerts[netI].tVertIdx:
                        netVerts.append(netI)
                    elif tVert == self.island.flatVerts[netJ].tVertIdx:
                        netVerts.append(netJ)
                    pass
        return netVerts, mapping

    def getNewBasisInfo(self, oldBasisInfo, testEdgeIdx, myMesh):
        faceIdx, edgeIdx, tVertIdx = oldBasisInfo
        newFaceIdx = myMesh.getOtherFaceIdx(testEdgeIdx, faceIdx)
        newEdgeIdx = testEdgeIdx
        newTVertIdx = myMesh.mesh.TopologyEdges.GetTopologyVertices(
            testEdgeIdx).I  # convention: useI
        return Basis(newFaceIdx, newEdgeIdx, newTVertIdx)

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




    
