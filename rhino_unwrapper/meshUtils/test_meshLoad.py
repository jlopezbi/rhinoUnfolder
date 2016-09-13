import unittest
import Rhino.Geometry
import rhinoscriptsyntax as rs

import meshLoad
reload(meshLoad)


def setUpModule():
    print("---- meshLoad ----")

def tearDownModule():
    print("---- module torn down ----")
    remove_objects()

def remove_objects():
    rs.DeleteObjects(rs.AllObjects())

class FileImporterTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        rs.DeleteObjects(rs.AllObjects())

    def test_import_file(self):
        importer = meshLoad.FileImporter()
        importer.import_file("/TestMeshes/blob")

    def test_non_existant_file(self):
        importer = meshLoad.FileImporter()
        self.assertRaises(AssertionError,importer.import_file,"/asdfasf/asdf")

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

