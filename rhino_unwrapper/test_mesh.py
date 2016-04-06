import unittest
import rhinoscriptsyntax as rs
import mesh
import scriptcontext
reload(mesh)

def make_test_mesh():
    vertices = []
    vertices.append((0.0,0.0,0.0))
    vertices.append((5.0, 0.0, 0.0))
    vertices.append((10.0, 0.0, 0.0))
    vertices.append((0.0, 5.0, 0.0))
    vertices.append((5.0, 5.0, 0.0))
    vertices.append((10.0, 5.0, 0.0))
    vertices.append((0.0, 10.0, 0.0))
    vertices.append((5.0, 10.0, 0.0))
    vertices.append((10.0, 10.0, 0.0))
    faceVertices = []
    faceVertices.append((0,1,4,4))
    faceVertices.append((2,4,1,1))
    faceVertices.append((0,4,3,3))
    faceVertices.append((2,5,4,4))
    faceVertices.append((3,4,6,6))
    faceVertices.append((5,8,4,4))
    faceVertices.append((6,4,7,7))
    faceVertices.append((8,7,4,4))
    mesh_GUID = rs.AddMesh( vertices, faceVertices )
    obj = scriptcontext.doc.Objects.Find(mesh_GUID)
    return obj.Geometry

class MeshTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mesh = mesh.Mesh(make_test_mesh())

    def test_get_set_of_edges(self):
        self.assertEqual(self.mesh.get_set_of_edges(),set(range(16)))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(MeshTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

