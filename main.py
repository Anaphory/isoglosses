#!/usr/bin/python

"""Simulate isoglosses-based language evolution forward in time"""

import itertools as it
import collections

import networkx


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


""" Write a function that generates “Cognate set lists” (abstractly,
without the actual cognate forms) based on:

1 maximal planar graph
for each meaning:
[  set of isoglosses
    planar convex subgraph
    date
]
  rate of isoglosses
distribution of isogloss sizes/isogloss shapes depending on time depth.
  First idea: Time depth here is relative to the age of the oldest non-trivial isogloss
for each language (node in planar graph)

Once that is a thing:

Following steps:
(1) Run some simulations to see whether they look reasonable
(2) Compare simulation results with real data, try to calibrate
(3) Implement isogloss stack likelihoods
(3a) Investigate the effects of invisible isoglosses
(4) Check whether inference can use likelihoods to recover isoglosses
(5) Add steps to also infer other parameters
(6) Infer isoglosses
"""

import numpy

def generate_isogloss_size(number_nodes_in_graph, time_from_origin):
    """Draw a random isogloss size compatible with the current time.

    Observation: Old language splits are between a small and a big set
    of languages.  But even splitting into one half very early, and
    then always in halves (thus giving an unusually balanced tree),

    Time should be normalized so that the expected isogloss size for
    the *most recent* times is exactly one language.

    This distribution should have 0 as minimum, number_nodes_in_graph
    as maximum.

    """
    # c is chosen such that expected_number_of_languages_in_isogloss
    # for time_from_origin==1 should be 1
    c = -numpy.log(1/number_nodes_in_graph)
    
    expected_number_of_languages_in_isogloss = (
        number_nodes_in_graph * numpy.exp(-c * time_from_origin))

    p = expected_number_of_languages_in_isogloss/number_nodes_in_graph
    
    return numpy.random.binomial(number_nodes_in_graph, p)

def test_isogloss_sizes_end():
    N = 20
    log = []
    for i in range(1000):
        log.append(generate_isogloss_size(N, 1))
    assert 0.95 < numpy.mean(log) < 1.05


def test_isogloss_sizes_start():
    N = 20
    log = []
    for i in range(1000):
        assert generate_isogloss_size(N, 0) == N


def is_simply_connected(graph, nodebunch):
    ...
    return True


def neighbors(graph, nodebunch):
    neighbors = set()
    for node in nodebunch:
        for n in graph[node]:
            neighbors.add(n)
    return neighbors - set(nodebunch)


def random_subgraph_of_given_size(graph, size):
    """ Generate a random subgraph of the connected graph of given size.

    """
    # Draw a random node
    nodes = graph.nodes()
    while True:
        random_index = numpy.random.randint(len(nodes))
        nodebunch = [nodes[random_index]]
        while len(nodebunch) < size:
            adjacent_nodes = list(neighbors(graph, nodebunch))
            new_node_index = numpy.random.randint(len(adjacent_nodes))
            nodebunch.append(adjacent_nodes[new_node_index])
        if is_simply_connected(graph, nodebunch):
            return nodebunch


g = networkx.Graph([
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 2), (1, 3), (1, 4), (2, 3), (3, 4),
        (5, 0), (5, 1), (5, 2)])


def test_random_subgraphs():
    counter = collections.Counter()
    for _ in range(1000):
        nodes = random_subgraph_of_given_size(g, 3)
        for node in nodes:
            counter[node] += 1
    print(counter)


def test_neighbors():
    assert neighbors(g, [3, 4]) == {0, 1, 2}


def single_meaning_simulation(graph, meaning_rate=10):
    meanings = {node: 0 for node in graph}
    next_isogloss = 1
    t = 0
    while t < 1:
        next_time_step = numpy.random.exponential(1/meaning_rate)
        t += next_time_step
        size = generate_isogloss_size(len(g), t)
        isogloss = random_subgraph_of_given_size(graph, size)
        for node in isogloss:
            meanings[node] = next_isogloss
        next_isogloss += 1
        print(t, isogloss)
    return meanings
