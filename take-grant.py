import json
import networkx as nx
import multiprocessing as mp
from matplotlib import pyplot as plt
from itertools import product

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
TG_PATH_TYPES = [TAKE, GRANT]


def read_graph(filename: str) -> tuple[nx.MultiDiGraph, dict[str, str], dict[str, str]]:
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
    edges_to_labels = {}
    for edge in edges:
        id_attrs.append((edge[SOURCE], edge[TARGET], edge[ID], edge))
        edges_to_labels[(edge[SOURCE], edge[TARGET])] = edge[EDGE_TYPE]
    graph.add_edges_from(id_attrs)

    return graph, nodes_to_labels, edges_to_labels


def print_graph(graph: nx.MultiDiGraph, nodes_to_labels: dict[str, str], edges_to_labels: dict[tuple, str]):
    plt.subplot(111)
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos=pos, with_labels=True, labels=nodes_to_labels)
    nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edges_to_labels)
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


def initially_spans(graph: nx.MultiDiGraph, x: str) -> set[str]:
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


def terminally_spans(graph: nx.MultiDiGraph, s_ids: set[str]) -> set[str]:
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


def get_edge_data(graph: nx.MultiDiGraph, u: str, v: str, key: str) -> dict[str, str] | None:
    edge = graph.get_edge_data(u, v, key)
    if not edge:
        return graph.get_edge_data(u, v, key)
    return edge


def is_island_bridge(
        graph: nx.MultiDiGraph, edge: dict[str, str], node: str,
        prev_edge: dict[str, str] | None, prev_node: str) -> bool:

    if edge != None:
        e_src, e_tgt, e_data = edge[SOURCE], edge[TARGET], edge
    else:
        return False

    if prev_edge != None:
        pe_src, pe_tgt, pe_data = prev_edge[SOURCE], prev_edge[TARGET], prev_edge

    # only tg-paths allowed
    if e_data.get(EDGE_TYPE) not in TG_PATH_TYPES:
        return False

    # start of the tg-path
    if prev_edge == None:
        if graph.nodes[node][NODE_TYPE] == SUBJECT:
            return True
        return False
    elif pe_data.get(EDGE_TYPE) not in TG_PATH_TYPES:
        return False

    # island
    if graph.nodes[prev_node][NODE_TYPE] == SUBJECT or graph.nodes[node][NODE_TYPE] == SUBJECT:
        return True

    # bridge paths are { t→* , t←*, t→* g→ t←*, t→* g← t←* }
    #
    # t→* path can be extended by GRANT edge or other t→* path
    if pe_src == prev_node and pe_data[EDGE_TYPE] == TAKE:
        if e_data[EDGE_TYPE] == GRANT:
            return True
        elif e_data[EDGE_TYPE] == TAKE and e_src == node:
            return True
        return False
    # t←* paths can be extended only by themselves
    elif pe_tgt == prev_node and pe_data[EDGE_TYPE] == TAKE:
        if e_tgt == node and e_data[EDGE_TYPE] == TAKE:
            return True
        return False
    # only t←* paths allowed after GRANT edge
    elif pe_data[EDGE_TYPE] == GRANT:
        if e_tgt == node and e_data[EDGE_TYPE] == TAKE:
            return True
        return False

    return False


def is_island_bridge_path(args: tuple[nx.MultiDiGraph, nx.MultiGraph, tuple[str, str]]) -> bool:
    graph, graph_view, xi_si = args
    xi, si = xi_si

    paths = nx.all_simple_edge_paths(graph_view, xi, si)
    for path in paths:
        prev_edge = None
        for prev_node, curr_node, edge_id in path:
            edge = get_edge_data(graph, prev_node, curr_node, edge_id)
            ok = is_island_bridge(
                graph, edge, curr_node, prev_edge, prev_node)
            if not ok:
                break
            prev_edge = edge
        # return True 
        # todo: bug
    return False


def can_share(graph: nx.MultiDiGraph, a: str, x: str, y: str) -> bool:

    # condition 1
    edges_x_y = graph.get_edge_data(x, y)
    for edge_data in edges_x_y.values():
        if edge_data[EDGE_TYPE] == a:
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
    args = [(graph, undirected_graph_view, xi_si)
            for xi_si in product(xi_ids, si_ids)]
    with mp.Pool() as pool:
        ress = pool.imap_unordered(is_island_bridge_path, args)
        for res in ress:
            if res:
                return True
    return False


g, nodes_to_labels, edges_to_labels = read_graph('takegrant_example.json')
# print_graph(g, nodes_to_labels, edges_to_labels)
print(can_share(graph=g, a='READ', x='e6c588de-9f16-46a0-bd22-c96f76873911',
      y='d9f8d86c-48a9-4ffc-a122-26da3f3452eb'))
