from rhino_unwrapper.commands import unwrap
from rhino_unwrapper.rhino_helpers import getMesh

# Reload modules each time during development
import sys
modules = ['commands', 'graph', 'layout', 'rhino_helpers', 'transformations', 'visualization']
for module in modules:
  reload(sys.modules['rhino_unwrapper.'+module])

__commandname__ = "Unwrap"
def RunCommand( is_interactive ):
  mesh = getMesh("Select mesh to unwrap")
  if mesh:
    unwrap(mesh)

if __name__=="__main__":
  RunCommand(True)