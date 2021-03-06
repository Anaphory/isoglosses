#!/usr/bin/python

"""Simulate isoglosses-based language evolution forward in time"""

import itertools as it
import collections

import numpy
import networkx
import scipy.spatial as spt

import matplotlib
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


def display_history(history, graph, node_order=None):
    if node_order is None:
        node_order = sorted(graph.node)
    print(" "*6, " ".join(["{:2}".format(node) for node in node_order]))
    for time, languages, center in history:
        binary = " ".join(["{:2}".format("X" if i in languages else " ")
                           for i in node_order])
        print("{:6.3f}".format(time), binary, "{:4d}".format(len(languages)), center)


g_small = networkx.Graph([
    ("A", "B"), ("A", "C"), ("A", "D"), ("A", "E"),
    ("B", "C"), ("B", "D"), ("B", "E"), ("C", "D"), ("D", "E"),
    ("F", "A"), ("F", "B"), ("F", "C")])

chain_length = 6
g_chain = networkx.Graph([
    (i, i+1) for i in range(chain_length-1)
])
xy_chain = [
    (numpy.sin(2 * numpy.pi * i / chain_length),
     numpy.cos(2 * numpy.pi * i / chain_length))
    for i, n in enumerate(g_chain.nodes)]


# g = g_chain
# xy = xy_chain

try:
    g
except:
    g, xy = delaunay_graph(20)
    plt.axis('equal')
    networkx.draw_networkx(g, pos=xy, with_labels=True, node_color="y")
    plt.show(block=False)


def to_nearly_square_array_factory(size):
    """Create a function that turns a list of length size into a nearly square array.

    Nearly square arrays here means that the first axis is ⌈√s⌉, the second
    axis is ⌈s/√s⌉. The last few cells will be padded using NaN.

    """
    axis_one = int(size ** 0.5)
    if size % axis_one:
        axis_one += 1
    axis_two = size // axis_one
    if size % axis_one:
        axis_two += 1
    gaps = [numpy.nan] * (axis_one * axis_two - size)
    def to_nearly_square_array(l):
        return numpy.reshape(l + gaps, (axis_one, axis_two))
    return to_nearly_square_array


def sort_centrality(graph):
    nodes = list(graph.node)
    distances = {}
    for source, length_by_target in networkx.shortest_path_length(graph, weight='length'):
        distances[source] = sum([x**2 for x in length_by_target.values()])
    return sorted(nodes, key=distances.get)


def distance(language0, language1):
    return (numpy.array(language0) == numpy.array(language1)).sum()/len(language0)



for t_max in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000):
    plt.figure()
    labels = networkx.draw_networkx_labels(g, pos=xy, with_labels=True, cmap=plt.get_cmap('jet'))

    # Simulate meanings
    meaning_maps = {node: [] for node in g.node}
    for meaning in sorted(numpy.random.gamma(1, 1, size=64)):
        meanings, history = single_meaning_simulation(g, meaning_rate=meaning, t_max=t_max)
        display_history(history, g, node_order=sort_centrality(g))
        isoglosses = sorted(set(meanings.values()))
        for node in g.node:
            meaning_maps[node].append(isoglosses.index(meanings[node]))

    # Draw edges proportional to overlap
    if g == g_chain:
        for n0, n1 in it.combinations(g, 2):
            g.add_edge(n0, n1)
    edge_widths = [5*distance(meaning_maps[node0], meaning_maps[node1])
                for node0, node1 in g.edges]
    edges = networkx.draw_networkx_edges(g, pos=xy, with_labels=True,
                                        width=edge_widths)

    cmap = matplotlib.colors.ListedColormap(
            [(0, 0, 0.6),
            (0, 0, 0),
            (0, 0, 0),
            (0.5, 0.5, 0.5),
            (1, 1, 1,),
            (1, 1, 1,),
            (1, 1, 0.5)],
            name='extremes')

    square = to_nearly_square_array_factory(len(meaning_maps[node]))
    ax = plt.gca()
    for node in g.node:
        pos = xy[node]
        xx, yy = ax.transData.transform(pos)
        xa, ya = plt.gcf().transFigure.inverted().transform((xx, yy))
        a = plt.axes([xa - 0.02, ya - 0.02, 0.04, 0.04])
        a.axis('off')
        a.matshow(square(meaning_maps[node]), cmap=cmap)

    # plt.colorbar(nodes)
    plt.show(block=False)

    plt.figure()
    distances = []
    overlap = []
    for (i0, n0), (i1, n1) in it.combinations(enumerate(g), 2):
        x0, y0 = xy[i0]
        x1, y1 = xy[i1]
        distances.append(((x0-x1)**2 + (y0-y1)**2)**0.5)
        overlap.append(distance(meaning_maps[n0], meaning_maps[n1]))

    plt.scatter(distances, overlap, alpha=0.3)
    plt.ylim((0, 1))
    plt.savefig("scatter_{:}.png".format(t_max))
    plt.show(block=False)
