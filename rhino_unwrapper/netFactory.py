import rhinoscriptsyntax as rs
import scriptcontext
import random,inspect
import weight_functions as wf
import mesh as m
import layout as la

reload(wf)
reload(la)
reload(m)

def all_weight_functions():
    return dict([m for m in inspect.getmembers(wf, inspect.isfunction)])




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
        net.drawEdges_simple()
        return net
    
    
if __name__=="__main__":
    loader = fileImporter()
    getter = meshGetter()
    myMesh = m.Mesh(getter.getSelectedMesh())
    weightFunc = all_weight_functions()["edgeAngle"]
    unfolder = la.UnFolder()
    netMaker = NetMaker(myMesh,weightFunc,unfolder,None)
    net = netMaker.makeNet()


