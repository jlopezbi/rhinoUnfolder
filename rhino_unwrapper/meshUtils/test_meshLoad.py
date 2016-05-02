import unittest,os,sys
path = "/Users/josh/Library/Application Support/McNeel/Rhinoceros/Scripts/rhinoUnfolder/rhino_unwrapper/"
#sys.path.append(path)

import meshLoad
reload(meshLoad)

class FileImporterTestCase(unittest.TestCase):
    def test_loadFile(self):
        importer = meshLoad.FileImporter()
        importer.loadFile("/TestMeshes/blob")

#class MeshLoadTestCase(unittest.TestCase):
#    def test_load_mesh(self):
#        meshLoad.load_mesh("/TestMeshes/blob")


if __name__ == '__main__':
    file_name = os.path.basename(__file__).split('.')[0]
    unittest.main(verbosity=2,module=file_name,exit=False)

