import unittest
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs

import transformations as trans
import unfold
import mesh
import Map
import Net
import meshLoad

reload(meshLoad)
reload(Net)
reload(unfold)
reload(trans)
reload(mesh)
reload(Map)

#TODO: test unfolding of full mesh, creating a net with multiple islands

class CatsTestCase(unittest.TestCase):

    def test_CATS(self):
        pass
