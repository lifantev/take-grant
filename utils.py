import json
import networkx as nx
from matplotlib import pyplot as plt

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
    with open(filename, 'r') as file:
        json_graph = json.load(file)
        nodes = json_graph[GRAPH][NODES]
        edges = json_graph[GRAPH][EDGES]

    graph = nx.MultiDiGraph()
    id_attrs = ((node[ID], node) for node in nodes)
    nodes_to_labels = {node[ID]: node[LABEL] for node in nodes}
    graph.add_nodes_from(id_attrs)

    id_attrs = ((edge[SOURCE], edge[TARGET], edge[ID], edge) for edge in edges)
    edges_to_labels = {(edge[SOURCE], edge[TARGET])
                        : edge[EDGE_TYPE] for edge in edges}
    graph.add_edges_from(id_attrs)

    return graph, nodes_to_labels, edges_to_labels


def print_graph(graph: nx.MultiDiGraph, filename: str, nodes_to_labels: dict[str, str], edges_to_labels: dict[tuple, str]):
    f = plt.figure(figsize=(20, 20))
    f.tight_layout()
    plt.subplot(111)
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos=pos, with_labels=True, labels=nodes_to_labels)
    nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edges_to_labels)
    plt.savefig(filename)
