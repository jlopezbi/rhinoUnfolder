# STRUCTURE


## CLASSES
* Layout
* Net
* FlatEdge
* FlatVert
* FlatFace

What if there was a Mesh class that contained utilites for getting info on the mesh. Then layout would just know that there is a mesh object that responds to various messages

Mesh:
attributes: rhino mesh object
methods:
	* getOtherFace(edge,face)
	* getTVertsForVert
etc.
Lets do it.
