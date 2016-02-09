import rhinoscriptsyntax as rs


class MeshLoader(object):

    def __init__(self):
        pass

    def loadMesh(self):
       rs.Command("-_import " + "testGeom/testSuite" + " _Enter")

    def test(self):
        self.loadMesh()
        pass

if __name__=="__main__":
    loader = MeshLoader()
    loader.loadMesh()
