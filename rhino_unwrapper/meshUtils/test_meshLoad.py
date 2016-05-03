import unittest,os,sys
import Rhino.Geometry
import rhinoscriptsyntax as rs
#path = "/Users/josh/Library/Application Support/McNeel/Rhinoceros/Scripts/rhinoUnfolder/rhino_unwrapper/"
#sys.path.append(path)

import meshLoad
reload(meshLoad)


def tearDownModule():
    print "MODULE TORN DOWN"
    rs.DeleteObjects(rs.AllObjects())

class FileImporterTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        rs.DeleteObjects(rs.AllObjects())

    def test_import_file(self):
        importer = meshLoad.FileImporter()
        importer.import_file("/TestMeshes/blob")

class SelectMeshTestCase(unittest.TestCase):
    def setUp(self):
        meshLoad.FileImporter().import_file("/TestMeshes/blob")

    def tearDown(self):
        rs.DeleteObjects(rs.AllObjects())

    def test_user_selects_mesh_and_get_mesh_back(self):
        mesh = meshLoad.user_select_mesh()
        self.assertIsInstance(mesh,Rhino.Geometry.Mesh)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(SelectMeshTestCase))
    suite.addTest(loader.loadTestsFromTestCase(FileImporterTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

