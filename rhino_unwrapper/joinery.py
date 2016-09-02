import rhinoscriptsyntax as rs


def rivet_positions(curve_id,offset,length):
    '''

       |  |  |  |  |  |  |  |
    I------------------------->J

    '''
    base_points = rs.DivideCurveLength(curve_id,length, create_points=True, return_points=True)
    #get edge veec
    #NOTE: Currentlt working here!
    for point in base_points:
        pass



class Tab(object):

    def __init__(self):
        self.tab_width = tab_width

class RivetSystem(object):
    def __init__(self,hole_offset,rivet_diameter):
        self.hole_offset = hole_offset
        self.rivet_diameter = rivet_diameter

    def create_holes(self):
        pass

    def create_tabs(self):
        pass


