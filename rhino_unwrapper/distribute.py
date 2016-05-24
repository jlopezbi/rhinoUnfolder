''' Distributes islands in a net so that they can be edited and looked at easily'''

def spread_out_islands_horizontally(net):
    islands = net.get_island_list()
    for i,island in enumerate(islands):
        if i!=0:
            island.move_to_edge(islands[i-1])

