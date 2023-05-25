import logging as log
import multiprocessing as mp
import networkx as nx

from itertools import product
from utils import *

log.basicConfig(format='%(process)d-%(levelname)s-%(message)s',
                level=log.DEBUG, filename='./log/take_grant.log', filemode='w')


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
    g_to_x = {src for src, _, d in graph.in_edges(
        nbunch=x, data=True) if d[EDGE_TYPE] == GRANT}

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
    try:
        return graph[u][v][key]
    except KeyError:
        try:
            return graph[v][u][key]
        except [KeyError]:
            return None


def is_island_bridge_subpath(
        graph: nx.MultiDiGraph, edge: dict[str, str], node: str,
        prev_edge: dict[str, str] | None, prev_node: str) -> bool:

    if edge is not None:
        _, e_tgt, e_data = edge[SOURCE], edge[TARGET], edge
    else:
        return False

    if prev_edge is not None:
        pe_src, pe_tgt, pe_data = prev_edge[SOURCE], prev_edge[TARGET], prev_edge

    # only tg-paths allowed
    if e_data.get(EDGE_TYPE) not in TG_PATH_TYPES:
        return False

    # start of the tg-path
    if prev_edge is None:
        if graph.nodes[prev_node][NODE_TYPE] == SUBJECT:
            return True
        return False
    elif pe_data.get(EDGE_TYPE) not in TG_PATH_TYPES:
        return False

    # island
    if graph.nodes[prev_node][NODE_TYPE] == SUBJECT:
        return True

    # bridge paths are { t→* , t←*, t→* g→ t←*, t→* g← t←* }
    #
    # t→* path can be extended by GRANT edge or other t→* path
    if pe_tgt == prev_node and pe_data[EDGE_TYPE] == TAKE:
        if e_data[EDGE_TYPE] == GRANT:
            return True
        elif e_data[EDGE_TYPE] == TAKE and e_tgt == node:
            return True
        return False
    # t←* paths can be extended only by themselves
    elif pe_src == prev_node and pe_data[EDGE_TYPE] == TAKE:
        if e_tgt == prev_node and e_data[EDGE_TYPE] == TAKE:
            return True
        return False
    # only t←* paths allowed after GRANT edge
    elif pe_data[EDGE_TYPE] == GRANT:
        if e_tgt == prev_node and e_data[EDGE_TYPE] == TAKE:
            return True
        return False

    return False


def island_bridge_paths_exist(args: tuple[nx.MultiDiGraph, nx.MultiGraph, tuple[str, str]]) -> bool:
    graph, graph_view, xi_si = args
    xi, si = xi_si
    log.info('[is_island_bridge_path: xi=%s, si=%s]', xi, si)

    def is_island_bridge_path(path: tuple[str, str, any]) -> bool:
        prev_edge = None
        ok_path = True
        for prev_node, curr_node, edge_id in path:
            edge = get_edge_data(graph, prev_node, curr_node, edge_id)
            ok = is_island_bridge_subpath(
                graph, edge, curr_node, prev_edge, prev_node)
            log.debug('[is_island_bridge_path:xi=%s, si=%s] prev_node=%s, curr_node=%s, ok=%s',
                      xi, si, prev_node, curr_node, ok)
            if not ok:
                ok_path = False
                break
            prev_edge = edge

        log.info('[is_island_bridge_path:xi=%s, si=%s] ok_path=%s',
                 xi, si, ok_path)
        return ok_path

    paths = nx.all_simple_edge_paths(graph_view, xi, si)
    for path in paths:
        log.info('[is_island_bridge_path:xi=%s, si=%s] path=%s', xi, si, path)
        if is_island_bridge_path(path):
            return True
    return False


def x_y_a_edge_exist(graph: nx.MultiDiGraph, a: str, x: str, y: str) -> bool:
    x_y_edge = graph.get_edge_data(x, y)
    if x_y_edge is not None and any(edge_data[EDGE_TYPE] == a for edge_data in x_y_edge.values()):
        return True
    return False


def s_y_a_nodes(graph: nx.MultiDiGraph, a: str, y: str) -> set[str]:
    s_ids = set()
    for src, _, d in graph.in_edges(nbunch=y, data=True):
        if d[EDGE_TYPE] == a:
            s_ids.add(src)
    return s_ids


def can_share(graph: nx.MultiDiGraph, a: str, x: str, y: str) -> bool | None:
    if x == y:
        return None

    # condition 1
    if x_y_a_edge_exist(graph, a, x, y):
        log.info('[can_share:condition #1] true')
        return True

    # condition 2
    s_ids = s_y_a_nodes(graph, a, y)
    log.info('[can_share:condition #2] s_ids=%s', s_ids)
    if not s_ids:
        return False

    # condition 3.1
    xi_ids = initially_spans(graph, x)
    log.info('[can_share:condition #3.1] xi_ids=%s', xi_ids)
    if not xi_ids:
        return False

    # condition 3.2
    si_ids = terminally_spans(graph, s_ids)
    log.info('[can_share:condition #3.2] si_ids=%s', si_ids)
    if not si_ids:
        return False

    # condition 4
    undirected_graph_view = graph.to_undirected(as_view=True)
    args = ((graph, undirected_graph_view, xi_si)
            for xi_si in product(xi_ids, si_ids))
    with mp.Pool() as pool:
        for res in pool.imap_unordered(island_bridge_paths_exist, args):
            if res:
                return True
    return False
