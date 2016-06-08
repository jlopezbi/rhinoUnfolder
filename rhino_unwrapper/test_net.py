import unittest
import Net
import transformations as trans
import Rhino.Geometry as geom
import rhinoscriptsyntax as rs

reload(Net)
reload(trans)

def setUpModule():
    print("---- net ----")

def tearDownModule():
    print("---- module torn down ----")
    remove_objects()

def remove_objects():
    rs.DeleteObjects(rs.AllObjects())

class StubbedIsland(object):
    def __init__(self):
        self.group_name = rs.AddGroup()
        self.line_guid = rs.AddLine((0,0,0),(5,5,0))
        rs.AddObjectToGroup(self.line_guid,self.group_name)

class NetTestCase(unittest.TestCase):
    def setUp(self):
        self.net = Net.Net()
        self.net.add_island(StubbedIsland())

    def _test_get_island_for_group(self):
        '''
        To be correctly tested later; when user-input segmentation and
        joining becomes the current focus
        '''
        islands = self.net.get_island_list()
        correct_island = islands[0]
        line_guid = correct_island.line_guid
        island = self.net.get_island_for_line(line_guid)
        self.assertEqual(island,correct_island)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(NetTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)
