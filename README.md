rhinoUnfolder
==============

A Python plugin to Rhino that unfolds meshes.

You can use it to create flat, foldable versions of your 3D models. It's like [Pepakura](http://www.tamasoft.co.jp/pepakura-en/) for Rhino.

How To Run
----------

1. [Install Rhino and RhinoPython](http://python.rhino3d.com/content/118-Getting-Started-1-quot-Hello-Rhino-quot)
2. Download this repository and save it to your Rhino 'Scripts' directory:
  `git clone https://github.com/jlopezbi/rhinoUnwrapper.git`
3. Execute 'RunPythonScript' from Rhino
4. Select 'Unwrap_cmd.py' from the rhinoUnwrapper directory


Status
------

rhinoUnfolder is alpha software—it isn't finished yet. Don't expect it to work for you.

**Basic mesh unwrapping is working**!

Also, it can only unwrap relatively simple meshes with few areas of high curvature. It uses a face-angle weight function. Try adding new weight functions for higher quality unfoldings.
