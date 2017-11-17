#!/usr/bin/python

"""Simulate isoglosses-based language evolution forward in time"""

import itertools as it
import collections

import networkx
import scipy.spatial as spt

import matplotlib.pyplot as plt

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



import numpy

def expected_number_of_languages_in_isogloss(time_from_origin,
                                             number_nodes_in_graph):
    """Calculate the expected number of languages in an isogloss"""
    # c is chosen such that expected_number_of_languages_in_isogloss
    # for time_from_origin==1 should be 1
    c = -numpy.log(1/number_nodes_in_graph)

    return (
        number_nodes_in_graph * numpy.exp(-c * time_from_origin))


def expected_radius_of_isogloss(time_from_origin, graph_diameter=1):
    """Calculate the expected number of languages in an isogloss"""
    # Half life of social influence $t$ to be taken from social
    # psychology literature
    t = 30

    return (
        graph_diameter * numpy.exp(-time_from_origin/t * numpy.log(2)))


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
    p = (expected_number_of_languages_in_isogloss(
        time_from_origin, number_nodes_in_graph)
         / number_nodes_in_graph)

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


def random_disk_of_given_radius(graph, radius):
    """Generate a random disk subgraph of the connected graph of given size

    “Disk” here means that we always add the node that is closest to
    the nodes already included.

    """
    nodes = list(graph.node)
    random_index = numpy.random.randint(len(nodes))
    center = nodes[random_index]
    distances = {center: 0}
    while True:
        adjacent_nodes = list(neighbors(graph, distances))
        target = None
        target_distance = numpy.inf
        for node in adjacent_nodes:
            distance = numpy.inf
            for edge_to, edge_properties in graph[node].items():
                # edge is a dictionary mapping a neighbor to a dict of edge properties
                if edge_to in distances:
                    via_distance = (distances[edge_to]
                                    + edge_properties.get(
                                        "length", numpy.random.random() * 2))
                    if via_distance < distance:
                        distance = via_distance
            if distance < target_distance:
                target = node
                target_distance = distance
        if target_distance > radius:
            break
        distances[target] = target_distance
    return distances


def delaunay_graph(n):
    xy = numpy.random.normal(size=(n, 2))
    d = spt.Delaunay(xy)
    g = networkx.Graph()
    for p1, p2, p3 in d.simplices:
        g.add_edge(p1, p2, length=spt.distance.euclidean(xy[p1], xy[p2]))
        g.add_edge(p1, p3, length=spt.distance.euclidean(xy[p1], xy[p3]))
        g.add_edge(p2, p3, length=spt.distance.euclidean(xy[p2], xy[p3]))
    return g, xy


def test_random_subgraphs():
    counter = collections.Counter()
    for _ in range(1000):
        nodes = random_subgraph_of_given_size(g, 3)
        for node in nodes:
            counter[node] += 1
    print(counter)


def test_random_disk():
    counter = collections.Counter()
    for _ in range(1000):
        nodes = random_disk_of_given_radius(g, numpy.random.random())
        for node in nodes:
            counter[node] += 1
    print(counter.most_common())


def test_neighbors():
    assert neighbors(g, [3, 4]) == {0, 1, 2}


def diameter(graph):
    """Calculate the diameter of the graph.

    Edge lengths are assumed to be in the 'length' attribute.
    """
    max_l = 0
    for source, length_by_target in networkx.shortest_path_length(graph, weight='length'):
        max_l = max(max_l, *length_by_target.values())
    return max_l


def single_meaning_simulation(graph, meaning_rate=10, t_max=100):
    meanings = {node: 0 for node in graph}
    next_isogloss = 1
    t = 0

    history = []

    while True:
        next_time_step = numpy.random.exponential(1/meaning_rate)
        t += next_time_step
        if t > t_max:
            break
        # Mean of the `power(α)` distribution is α/(α+1). So, to get
        # mean e = expected_radius_of_isogloss for α=2:
        e = expected_radius_of_isogloss(t, diameter(graph))
        radius = numpy.random.power(2) * e * 1.5
        isogloss = random_disk_of_given_radius(graph, radius)
        for node in isogloss:
            meanings[node] = next_isogloss
            if isogloss[node] == 0:
                center = node
        next_isogloss += 1
        history.append((t, isogloss, center))
    return meanings, history


def check_single_meaning_simulation():
    m, d = single_meaning_simulation(g, 1000)

    old_i = 0
    for i in numpy.linspace(0, 1, 10):
        print(sum([len(isogloss) for t, isogloss in d
        if old_i < t <= i]))
        old_i = i


def display_history(history, graph):
    nodes = sorted(graph.node)
    print(" "*6, " ".join(["{:2}".format(node) for node in nodes]))
    for time, languages, center in history:
        binary = " ".join(["{:2}".format("X" if i in languages else " ")
                           for i in nodes])
        print("{:6.3f}".format(time), binary, "{:4d}".format(len(languages)), center)


g_small = networkx.Graph([
    ("A", "B"), ("A", "C"), ("A", "D"), ("A", "E"),
    ("B", "C"), ("B", "D"), ("B", "E"), ("C", "D"), ("D", "E"),
    ("F", "A"), ("F", "B"), ("F", "C")])

g_chain = networkx.Graph([
    (i, i+1) for i in range(20)
])
try:
    g
except:
    g, xy = delaunay_graph(20)
    plt.axis('equal')
    networkx.draw_networkx(g, pos=xy, with_labels=True, node_color="y")
    plt.show(block=False)


meanings, history = single_meaning_simulation(g)
display_history(history, g)
by_form = {}
for lect, form in meanings.items():
    by_form.setdefault(form, set()).add(lect)
print(by_form)
