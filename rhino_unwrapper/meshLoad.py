import rhinoscriptsyntax as rs
import scriptcontext
import random,inspect
import weight_functions as wf
import mesh as m
import unfold 

import os

reload(wf)
reload(unfold)
reload(m)

def all_weight_functions():
    return dict([m for m in inspect.getmembers(wf, inspect.isfunction)])

def load_mesh(meshFilePath=None):
    '''
    assumes that the file has only one mesh in it!
    puts the mesh in the meshFilePath file into the current document
    returns the rhino mesh and the mesh GUID
    '''
    importer = FileImporter()
    importer.loadFile(meshFilePath)
    getter = MeshGetter()
    mesh_guid = getter.getRandMeshGUID()
    mesh = getter.getGeomFromGUID(mesh_guid)
    return mesh

class FileImporter(object):
    """
    Loads a saved file
    """

    def __init__(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.prefix = "-_import " + chr(34)
        self.suffix = chr(34) + " _Enter"

    def loadFile(self,relPath=None):
        if relPath==None: 
            rs.Command("_import ")
            return
        abs_path = self.directory + relPath
        command = self.prefix + abs_path + self.suffix
        rs.Command(command)

class MeshGetter(object):

    def __init__(self):
        self.MeshID = 32


    def getRandMeshGUID(self):
        meshes = rs.ObjectsByType(self.MeshID)
        return random.choice(meshes)

    def getRandMesh(self,select=True):
        meshGuid = self.getRandMeshGUID()
        if select: rs.SelectObject(meshGuid)
        return self.getGeomFromGUID(meshGuid)

    def get_mesh_from_guid(self,guid):
        obj = scriptcontext.doc.Objects.Find(guid)
        return obj.Geometry

    def getSelectedMesh(self):
        selected = rs.SelectedObjects()
        for objId in selected:
            if rs.IsMesh(objId):
                return self.getGeomFromGUID(objId)
        return None

    def getGeomFromGUID(self,guid):
        obj = scriptcontext.doc.Objects.Find(guid)
        return obj.Geometry

class NetMaker(object):
    """
    creates a net
    """
    def __init__(self,myMesh,weightFunc,unfolder,cuts):
        self.myMesh = myMesh
        self.weightFunc = weightFunc
        self.unfolder = unfolder
        self.cuts = cuts

    def makeNet(self):
        dataMap,net,foldList = unfolder.unfold(self.myMesh,self.cuts,self.weightFunc)
        net.draw_edges()
        return net
    
    
if __name__=="__main__":
    meshFile= "/TestMeshes/blob"
    print load_mesh(meshFile)

