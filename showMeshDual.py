#Display a representation of the dual graph of a mesh

import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import System.Guid
import System.Drawing
from rhino_unwrapper.visualization import *
from rhino_unwrapper.rhino_inputs import *

mesh = getMesh("select a mesh")
distance = rs.GetReal("select distance for curves to buldge outwards",1,.001,100)

if distance and mesh:
  drawDualOfMesh(mesh,distance)