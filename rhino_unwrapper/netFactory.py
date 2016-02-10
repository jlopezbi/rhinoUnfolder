import rhinoscriptsyntax as rs
import scriptcontext
import random,inspect
import weight_functions as wf
import layout as la

reload(wf)
reload(la)



class fileImporter(object):
    """
    Loads a saved file
    """

    def __init__(self):
        pass

    def loadFile(self,filePath=None):
        if filePath==None: 
            rs.Command("_import ")
            return
        rs.Command("-_import " + filePath + " _Enter")

    def test(self):
        self.loadMesh("rhino_unwrapper/testMesh")

class meshGetter(object):

    def __init__(self):
        self.MeshID = 32

    def getRandMeshGUID(self):
        meshes = rs.ObjectsByType(self.MeshID)
        return random.choice(meshes)

    def getRandMesh(self,select=True):
        meshGuid = self.getRandMeshGUID()
        if select: rs.SelectObject(meshGuid)
        return self.getGeomFromGUID(meshGuid)

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
    
    def _getWeightFuncs(self):
        return dict([m for m in inspect.getmembers(wf, inspect.isfunction)])


if __name__=="__main__":
    loader = fileImporter()
    getter = meshGetter()
    mesh = getter.getRandMesh()
    #netMaker = NetMaker(mesh)


