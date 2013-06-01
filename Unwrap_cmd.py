from rhino_unwrapper.commands import unwrap
from rhino_unwrapper.rhino_helpers import getMesh

__commandname__ = "Unwrap"
def RunCommand( is_interactive ):
  mesh = getMesh("Select mesh to unwrap")
  if mesh:
    unwrap(mesh)

if __name__=="__main__":
  RunCommand(True)