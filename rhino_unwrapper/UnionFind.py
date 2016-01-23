#!/usr/bin/env python
 
# UnionFind.py
# Simple unoptimized union-find implementation
# Author: Evan Dempsey <evandempsey@gmail.com>
# Last Modified: 23/Dec/2012
 
class UnionFind(object):
    """Union-Find is a data structure for keeping track
    of partitions of sets into disjoint subsets"""
 
    def __init__(self,_disjointMode):
        """Set up leader and group dictionaries"""
        self.leader = {}  # maps member to group leader
        self.group = {}   # maps group leader to set of members
        self.disjointMode = _disjointMode
 
    def makeSet(self, elements):
        """Insert elements as new group"""
        assert type(elements) is list
 
        group = set(elements)
        self.group[elements[0]] = group
        for i in group:
            self.leader[i] = elements[0]
 
    def find(self, element):
        """Return the group associated with an element"""
        return self.leader[element]
    
    #added by JLB
    def getGroup(self,element):
        return self.group[self.find(element)]
 
    def union(self, element1, element2):
        """Merge the groups containing two different elements"""
        leader1 = self.leader[element1]
        leader2 = self.leader[element2]
 
        # If both elements are in same group, do nothing
        if self.disjointMode: #edit by JLB
            if leader1 == leader2:
                return
 
        # Otherwise, merge the two groups
        group1 = self.group[leader1]
        group2 = self.group[leader2]
 
        # Swap names if group1 is smaller than group2
        if len(group1) < len(group2):
            element1, leader1, group1, \
                element2, leader2, group2 = \
                element2, leader2, group2, \
                element1, leader1, group1
 
        # Merge group1 with group2, delete group2 and update leaders
        group1 |= group2
        del self.group[leader2]
        for i in group2:
            self.leader[i] = leader1
 
    def getNumGroups(self):
        """Return the number of groups"""
        return len(self.group)
         
def main():
    print "***Testing UnionFind***"
 
    unionFind = UnionFind()
    unionFind.makeSet([1])
    assert unionFind.getNumGroups() == 1
    unionFind.makeSet([2])
    assert unionFind.getNumGroups() == 2
    assert unionFind.find(1) == 1
    unionFind.union(1, 2)
    assert unionFind.getNumGroups() == 1
    assert unionFind.find(1) == 1
    assert unionFind.find(2) == 1
    unionFind.makeSet([23, 12, 3])
    assert unionFind.getNumGroups() == 2
    assert unionFind.find(12) == 23
    unionFind.union(2, 3)
    assert unionFind.getNumGroups() == 1
    assert unionFind.find(1) == 23
 
    print "All tests passed."
 
if __name__ == "__main__":
    main()
