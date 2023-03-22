import json
from matplotlib import pyplot as plt
import networkx as nx

GRAPH = 'graph'
NODES = 'nodes'
EDGES = 'edges'
ID = 'id'
LABEL = 'label'
SOURCE = 'source'
TARGET = 'target'
EDGE_TYPE = 'cclabel'
NODE_TYPE = 'active'
SUBJECT = 'SUBJECT'
OBJECT = 'OBJECT'
TAKE = 'TAKE'
GRANT = 'GRANT'


def read_graph(filename: str):
    json_graph = json.load(open(filename, 'r'))
    nodes = json_graph[GRAPH][NODES]
    edges = json_graph[GRAPH][EDGES]

    graph = nx.MultiDiGraph()

    id_attrs = []
    nodes_to_labels = {}
    for node in nodes:
        id_attrs.append((node[ID], node))
        nodes_to_labels[node[ID]] = node[LABEL]
    graph.add_nodes_from(id_attrs)

    id_attrs.clear()
    for edge in edges:
        id_attrs.append((edge[SOURCE], edge[TARGET], edge[ID], edge))
    graph.add_edges_from(id_attrs)

    return graph, nodes_to_labels


def print_graph(graph: nx.MultiDiGraph, nodes_to_labels: dict[str, str]):
    plt.subplot(111)
    nx.draw(graph, with_labels=True, labels=nodes_to_labels)
    plt.savefig('graph_view')


def dfs_for_spans(
        graph: nx.MultiDiGraph, ids: set[str],
        visited: set[str], to_visit: list[tuple[str, str]]):

    while to_visit:
        v, parent = to_visit.pop()
        if v not in visited:
            visited.add(v)
            if graph.nodes[v][NODE_TYPE] == SUBJECT:
                ids.add(v)
            for src, _, d in graph.in_edges(nbunch=v, data=True):
                if src != parent and d[EDGE_TYPE] == TAKE:
                    to_visit.append((src, v))


def initially_spans(x: str, graph: nx.MultiDiGraph):
    x_ids = set()
    # add x == x'
    x_node = graph.nodes.get(x)
    if x_node is not None and x_node[NODE_TYPE] == SUBJECT:
        x_ids.add(x)

    # if x' initially spans to x
    # get nodes that grant to x
    g_to_x = []
    for src, _, d in graph.in_edges(nbunch=x, data=True):
        if d[EDGE_TYPE] == GRANT:
            g_to_x.append(src)

    # t->* paths from subjects to grant nodes
    visited = set()
    to_visit = [(v, x) for v in g_to_x]
    dfs_for_spans(graph, x_ids, visited, to_visit)
    return x_ids


def terminally_spans(graph: nx.MultiDiGraph, s_ids: set[str]):
    si_ids = set()
    # add s == s', get nodes that take to s
    to_visit = []
    for s in s_ids:
        s_node = graph.nodes.get(s)
        if s_node is not None and s_node[NODE_TYPE] == SUBJECT:
            si_ids.add(s)
        for src, _, d in graph.in_edges(nbunch=s, data=True):
            if d[EDGE_TYPE] == TAKE:
                to_visit.append((src, s))

    # t->* paths from subjects to closest take nodes for s
    visited = set()
    dfs_for_spans(graph, si_ids, visited, to_visit)
    return si_ids


def can_share(a: str, x: str, y: str, graph: nx.MultiDiGraph):

    # condition 1
    edges_x_y = graph.get_edge_data(x, y)
    for edge in edges_x_y:
        if edge[EDGE_TYPE] == a:
            return True

    # condition 2
    s_ids = set()
    for src, _, d in graph.in_edges(nbunch=y, data=True):
        if d[EDGE_TYPE] == a:
            s_ids.add(src)
    if not s_ids:
        return False

    # condition 3.1
    x_ids = initially_spans(x, graph)
    if not x_ids:
        return False

    # condition 3.2
    si_ids = terminally_spans(graph, s_ids)
    if not si_ids:
        return False

    return False



g, nodes_to_labels = read_graph('takegrant_example.json')
print_graph(g, nodes_to_labels)
# print(g.nodes.get('5932ee46-5bc5-47a2-b90c-ef713d61cec8'))
