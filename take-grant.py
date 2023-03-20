import json
from matplotlib import pyplot as plt
import networkx as nx

def read_graph(filename: str):
    json_graph = json.load(open(filename, 'r'))
    nodes = json_graph['graph']['nodes']
    edges = json_graph['graph']['edges']

    g = nx.MultiDiGraph()

    id_attrs = []
    nodes_to_labels = {}
    for node in nodes:
        id_attrs.append((node['id'], node))
        nodes_to_labels[node['id']] = node['label']
    g.add_nodes_from(id_attrs)

    id_attrs.clear()
    for edge in edges:
        id_attrs.append((edge['source'], edge['target'], edge['id'], edge))    
    g.add_edges_from(id_attrs)

    return g, nodes_to_labels

def print_graph(g: nx.MultiDiGraph, nodes_to_labels: dict):
    plt.subplot(111)
    nx.draw(g, with_labels=True, labels=nodes_to_labels)
    plt.savefig('graph_view')


def can_share(a: str, x: str, y: str, g: nx.MultiDiGraph):
    edges_x_y = g.get_edge_data(x, y)
    for edge in edges_x_y:
        if edge['cclabel'] == a:
            return True

    return False


g, nodes_to_labels = read_graph('takegrant_example.json')
print_graph(g, nodes_to_labels)