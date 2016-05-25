import rhinoscriptsyntax as rs
import scriptcontext
import random,inspect,os
import Rhino


def load_mesh(meshFilePath=None):
    '''
    assumes that the file has only one mesh in it!
    puts the mesh in the meshFilePath file into the current document
    returns the rhino mesh and the mesh GUID
    '''
    rs.DeleteObjects(rs.AllObjects())
    importer = FileImporter()
    importer.import_file(meshFilePath)
    getter = MeshGetter()
    mesh_guids = getter.get_all_mesh_guids()
    mesh = getter.getGeomFromGUID(mesh_guids[0])
    return mesh

class FileImporter(object):
    """
    Loads a saved file
    """

    def __init__(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.prefix = "-_import " + chr(34)
        self.suffix = chr(34) + " _Enter"

    def import_file(self,relPath=None):
        if relPath==None: 
            rs.Command("_import ")
            return
        abs_path = self.directory + relPath
        command = self.prefix + abs_path + self.suffix
        did_work = rs.Command(command)
        assert did_work, "unable to import {}!".format(abs_path)

def user_select_mesh(message="select a mesh"):
    mesh_guid = rs.GetObject(message,filter=32,preselect=True)
    return get_geom_from_guid(mesh_guid)

def get_geom_from_guid(guid):
    obj = scriptcontext.doc.Objects.Find(guid)
    mesh =  obj.Geometry
    print mesh
    return mesh

def user_select_mesh_rhino_common(message="select a mesh"):
    getter = Rhino.Input.Custom.GetObject()
    getter.SetCommandPrompt(message)
    getter.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh
    getter.SubObjectSelect = True
    getter.Get()
    if getter.CommandResult() != Rhino.Commands.Result.Success:
        return
    objref = getter.Object(0)
    obj = objref.Object()
    mesh = objref.Mesh()
    obj.Select(False)
    if obj:
        return mesh

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

    def get_all_mesh_guids(self):
        return rs.ObjectsByType(self.MeshID)

    def getSelectedMesh(self):
        selected = rs.SelectedObjects()
        for objId in selected:
            if rs.IsMesh(objId):
                return self.getGeomFromGUID(objId)
        return None

    def getGeomFromGUID(self,guid):
        obj = scriptcontext.doc.Objects.Find(guid)
        return obj.Geometry

if __name__=="__main__":
    meshFile= "/TestMeshes/blob"
    print load_mesh(meshFile)

