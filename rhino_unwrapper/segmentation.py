from UnionFind import UnionFind

def segmentIsland(flatFaces,island):
  sets = UnionFind()
  if len(island)==0:
    island = range(len(flatFaces))
  for face in island:
    if face not in sets.leader.keys():
      sets.makeSet([face])
    neighbor = flatFaces[face].fromFace  
    if neighbor != None:
      if neighbor not in sets.leader.keys():
        sets.makeSet([neighbor])
      sets.union(face,neighbor)
  return sets.group, sets.leader

