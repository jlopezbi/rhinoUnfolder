import unittest
import Rhino.Geometry as geom
from ..cut import MeshSelecter

print type(goem.Mesh)

class SelectMeshTestCase(unittest.TestCase):
    def test_able_to_select_mesh(self):
        selecter = MeshSelecter()
        mesh = selecter.get_mesh()
        self.assertIsInstance(mesh,type(geom.Mesh))


