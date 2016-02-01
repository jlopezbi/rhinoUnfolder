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
-> done. much consequenses tracked down

16/01/31
Need to abstract edge representation to:
* joinery -> cut edges
* crease -> fold edges
* cut -> naked edges 
* utility. 
    (this one is just showing stuff so its easy to select or visulize, i.e.
    lines for each edge. Later selecton of crease or joinery geometry might be
    fine)

I have been mucking around in tab stuff, but really this needs to be abstracted
a bit.
each edge can have a type of joinery, crease or both.
Then its something like edge.displayJoinery() and edge.displayCrease()
Joinery could have:
    - both/single
    * tab
    * rivetHole
    * etc.
Crease:
    -mountain/valley
    * score
    * perforation
    * etc.

when a new cut gets formed of course it gets assigned joinery. The question of
two tabs or one is dealt with inside of this.
Of course eventually I want to optimize, i.e. do the halfwing mesh data struct
or the rhinocommon mesh for the net, but really stuff works right now. I just
need to build the abstractions necessary for custom geometry representation.

1) Build abstractions for custom geometry representation
2) make workflow efficient
    * joining segments
    * swaping which edge has joinery geom
    * saving cut patterns (maybe split command into two: 
        1) select cut edges 2) unfold
