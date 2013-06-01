from rhino_unwrapper.commands import unwrap
from rhino_unwrapper.rhino_helpers import getMesh, getOption

from rhino_unwrapper import weight_functions

# -RunPythonScript ResetEngine RhinoUnwrapper.Unwrap_cmd

from inspect import getmembers, isfunction

def all_weight_functions():
  return [m for m in getmembers(weight_functions, isfunction)]

__commandname__ = "Unwrap"
def RunCommand( is_interactive ):
  mesh = getMesh("Select mesh to unwrap")
  weightFunction = getOption(all_weight_functions(), "WeightFunction")
  if mesh and weightFunction:
    unwrap(mesh, weightFunction)

if __name__=="__main__":
  RunCommand(True)