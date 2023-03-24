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


def initially_spans(graph: nx.MultiDiGraph, x: str):
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


def get_edge_data(graph: nx.MultiDiGraph, u: str, v: str, key: str):
    edge = graph.get_edge_data(u, v, key)
    if not edge:
        return graph.get_edge_data(u, v, key)
    return edge


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
    xi_ids = initially_spans(graph, x)
    if not xi_ids:
        return False

    # condition 3.2
    si_ids = terminally_spans(graph, s_ids)
    if not si_ids:
        return False
    
    # condition 4
    undirected_graph_view = graph.to_undirected(as_view=True)
    for xi in xi_ids:
        for si in si_ids:
            for path in nx.all_simple_edge_paths(undirected_graph_view, xi, si):
                prev_edge = get_edge_data(path[0][0], path[0][1], path[0][2])
                for u, v, e_id in path[1:]:
                    edge = get_edge_data(graph, u, v, e_id)

                    return False

    return False


g, nodes_to_labels = read_graph('takegrant_example.json')
# print_graph(g, nodes_to_labels)
# print(nx.has_path(g.to_undirected(as_view=True),'a364bc99-3c63-416e-aff1-944447f6490b', 'e6c588de-9f16-46a0-bd22-c96f76873911' ))
# for path in nx.all_simple_edge_paths(g.to_undirected(as_view=True), 'a364bc99-3c63-416e-aff1-944447f6490b', 'e6c588de-9f16-46a0-bd22-c96f76873911'):
#     print(path)
# print(g.get_edge_data('b1b399db-f402-4e0d-b7c6-010105f4f261', 'b57685fb-928c-4d4a-a6f6-ac9392d82ca9', '6140db07-74b6-452c-a834-de39932ec283'))
