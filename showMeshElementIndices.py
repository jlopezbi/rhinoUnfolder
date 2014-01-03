#view face,edge or tVert indices of a mesh

import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import System.Guid
import System.Drawing
from rhino_unwrapper.visualization import *
from rhino_unwrapper.rhino_inputs import *

def viewIndices():
	mesh = getMesh("select mesh to view edgeIdxs")
	options = ['tverts','edges','faces']
	message = "type prefered entity"
	default = 'tverts'
	string = rs.GetString(message,'tverts',options)
	if string:
		geom = []
		if string == 'tverts':
			color = (0,255,0,255) #Magenta
			for vertIdx in range(mesh.TopologyVertices.Count):
				point = mesh.TopologyVertices.Item[vertIdx]
				drawTextDot(point,str(vertIdx),color)
				#rs.AddTextDot(str(vertIdx),point)
		elif string == 'edges':
			color = (0,0,255,0) #green
			for edgeIdx in range(mesh.TopologyEdges.Count):
				line = mesh.TopologyEdges.EdgeLine(edgeIdx)
				displayEdgeIdx(line,edgeIdx,color)
		elif string == 'faces':
			displayFaceIdxs(mesh)


if __name__=="__main__":
  viewIndices()