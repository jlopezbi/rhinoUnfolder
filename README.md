rhinoUnfolder
==============
A Python plugin to Rhino that unfolds meshes.

You can use it to create flat, foldable versions of your 3D models. It's like [Pepakura](http://www.tamasoft.co.jp/pepakura-en/) for Rhino.

Status
------
Working:
- selection of cuts, and cut-chains works.
- unfolding into multiple islands works.

Not working:
- editing net (segmentation and joining)

Notes For Developing
----------
do -RunPythonScript, reset engine, and then execute run_all_tests.py

How To Run
----------

1. [Install Rhino5 and RhinoPython](http://python.rhino3d.com/content/118-Getting-Started-1-quot-Hello-Rhino-quot)
2. Download this repository and save it to your Rhino 'Scripts' directory:
  `git clone https://github.com/jlopezbi/rhinoUnwrapper.git`
3. type `RunPythonScript` in rhino
4. Navigate to the rhinoUnfolder folder and select the protoype_cutAndUnfold.py script. The interactive  command will now run; follow the instructions as you would anothe rhino command.


