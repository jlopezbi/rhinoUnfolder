from rhino_unwrapper.commands import unwrap
from rhino_unwrapper.rhino_helpers import getMesh

# Reload modules each time during development
import sys, glob, os
modules = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"rhino_unwrapper/*.py")]
for module in modules:
  reload(sys.modules['rhino_unwrapper.'+module])

__commandname__ = "Unwrap"
def RunCommand( is_interactive ):
  mesh = getMesh("Select mesh to unwrap")
  if mesh:
    unwrap(mesh)

if __name__=="__main__":
  RunCommand(True)