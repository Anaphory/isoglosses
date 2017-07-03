#!/usr/bin/python

"""Simulate isoglosses-based language evolution forward in time"""

import networkx

def is_planar(G):
    """
    function checks if graph G has K(5) or K(3,3) as minors,
    returns True /False on planarity and nodes of "bad_minor"
    """
    result=True
    bad_minor=[]
    n=len(G.nodes())
    if n>5:
        for subnodes in it.combinations(G.nodes(),6):
            subG=G.subgraph(subnodes)
            if bipartite.is_bipartite(G):# check if the graph G has a subgraph K(3,3)
                X, Y = bipartite.sets(G)
                if len(X)==3:
                    result=False
                    bad_minor=subnodes
    if n>4 and result:
        for subnodes in it.combinations(G.nodes(),5):
            subG=G.subgraph(subnodes)
            if len(subG.edges())==10:# check if the graph G has a subgraph K(5)
                result=False
                bad_minor=subnodes
    return result,bad_minor

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

