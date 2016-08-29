#THIS_PROJECT STUFF
import transformations as trans
import Net as nt
import traversal as tr
import Map
import meshUtils.mesh as mesh
import weight_functions as wf
import islandMaker

#RHINO STUFF
import rhinoscriptsyntax as rs
import Rhino

#PYTHON STUFF
import collections,inspect

reload(trans)
reload(nt)
reload(tr)
reload(mesh)
reload(islandMaker)

def all_weight_functions():
    return dict([m for m in inspect.getmembers(wf, inspect.isfunction)])

def arbitrary_face_getter(canditate_faces):
    return canditate_faces.pop()


class UnFolder(object):
    """
    UnFolder is a class that unfolds a mesh by creating a net
    THIS IS THE NEW MAIN PLACE IN THE CODE!
    """

    def __init__(self,myMesh):
        self.myMesh  = myMesh
        self.dataMap = Map.Map(self.myMesh)
        self.net = nt.Net(self.myMesh)
        self.islandMaker = islandMaker.IslandMaker(self.dataMap, self.myMesh)
        self.processed_faces = set()

    def get_meshLoc_next_to_cut(self):
        assert self.myMesh.get_cuts() , "Mesh has no cuts set. Make sure to assign cuts first"
        canditate_faces = self.myMesh.get_set_of_face_idxs().difference(self.processed_faces)
        arbitrary_face = self.myMesh.get_face_next_to_a_cut()
        face_edges = self.myMesh.getFaceEdges(arbitrary_face)
        for edge in face_edges:
            if self.myMesh.is_cut_edge(edge) or self.myMesh.is_naked_edge(edge):
                loc = islandMaker.MeshLoc(arbitrary_face,edge)
                return loc
        raise AssertionError, "face {} did not have any cut edges, check that mesh has correct cut_edges".format(arbitrary_face)

    def unfold(self,start_loc=None):
        if start_loc == None:
            start_loc = self.get_meshLoc_next_to_cut()
        all_faces = self.myMesh.get_set_of_face_idxs()
        i = 0
        max_iters = len(all_faces)+1
        while self.processed_faces != all_faces:
            if i != 0:
                start_loc = self.get_meshLoc_next_to_cut()
            island,faces = self.islandMaker.make_island(start_loc)
            self.processed_faces.update(faces)
            self.net.add_island(island)
            i +=1
            if i >max_iters: 
                print("unfold() iterated {} or more times".format(max_iters))
                return
        return self.net

MeshLoc = collections.namedtuple('MeshLoc',['face','edge'])
IslandLoc = collections.namedtuple('IslandLoc',['face','edge']) #note face for island loc is prevFace

if __name__ == "__main__":
    unfolder = UnFolder()
    unfolder.unfold()


