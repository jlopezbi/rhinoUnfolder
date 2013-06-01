from rhino_helpers import getMesh
from rhino_unwrapper import unwrap

__commandname__ = "Unwrap"
def RunCommand( is_interactive ):
  mesh = getMesh("Select mesh to unwrap")
  if mesh:
    unwrap(mesh)