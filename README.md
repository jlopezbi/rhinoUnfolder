rhinoUnwrapper
==============

A Python plugin to Rhino that unwraps triangulated meshes

Install
-------

1. [Install Rhino and RhinoPython](http://python.rhino3d.com/content/118-Getting-Started-1-quot-Hello-Rhino-quot)
2. Download this repository and save it to your Rhino 'Scripts' directory
3. Execute 'RunPythonScript' from Rhino
4. Select 'unwrapmesh.py' from the rhinoUnwrapper directory


Status
------

rhinoUnwrapper is alpha software---it isn't finished yet.

**Basic mesh unwrapping is working**! However, you will need to modify the code to apply it to your own mesh.

Also, it can only unwrap relatively simple meshes with few areas of high curvature. It uses a face-angle weight function. Try adding new weight functions for higher quality unfoldings.
