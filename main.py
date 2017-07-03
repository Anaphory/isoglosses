#!/usr/bin/python

"""Simulate isoglosses-based language evolution forward in time"""

import itertools as it

import networkx
import networkx.bipartite as bipartite


def is_planar(G):
    """Check whether the graph G is planar

    Thes function checks if graph G has K(5) or K(3,3) as minors,
    returns True/False on planarity and the first nodes encountered
    that violate it, if any.

    """
    n = len(G.nodes())
    if n > 5:
        for subnodes in it.combinations(G.nodes(), 6):
            sub_graph = G.subgraph(subnodes)
            # check if the graph G has a subgraph K(3,3)
            if bipartite.is_bipartite(G):
                X, Y = bipartite.sets(G)
                if len(X) == 3:
                    return False, subnodes
    if n > 4:
        for subnodes in it.combinations(G.nodes(), 5):
            sub_graph = G.subgraph(subnodes)
            # check if the graph G has a subgraph K(5)
            if len(sub_graph.edges()) == 10:
                return False, subnodes
    return True, []


"""
1 maximal planar graph
for each meaning:
[  set of isoglosses
    planar convex subgraph
    date
]
  rate of isoglosses
distribution of isogloss sizes/isogloss shapes depending on time depth, relative to the age of the oldest language  
for each language (node in planar graph):
  date of birth
"""

