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

    g = nx.MultiDiGraph()

    id_attrs = []
    nodes_to_labels = {}
    for node in nodes:
        id_attrs.append((node[ID], node))
        nodes_to_labels[node[ID]] = node[LABEL]
    g.add_nodes_from(id_attrs)

    id_attrs.clear()
    for edge in edges:
        id_attrs.append((edge[SOURCE], edge[TARGET], edge[ID], edge))    
    g.add_edges_from(id_attrs)

    return g, nodes_to_labels

def print_graph(g: nx.MultiDiGraph, nodes_to_labels: dict):
    plt.subplot(111)
    nx.draw(g, with_labels=True, labels=nodes_to_labels)
    plt.savefig('graph_view')


def can_share(a: str, x: str, y: str, g: nx.MultiDiGraph):
    
    # condition 1
    edges_x_y = g.get_edge_data(x, y)
    for edge in edges_x_y:
        if edge[EDGE_TYPE] == a:
            return True

    # condition 2
    s_ids = []
    for s, _, d in g.in_edges(nbunch=y, data=True):
        if d[EDGE_TYPE] == a:
            s_ids.append(s)
    if not s_ids:
        return False
    
    # condition 3.1
    x_ids = []
    x_node = g.nodes.get(x) 
    if x_node is not None and x_node[NODE_TYPE] == SUBJECT:
        x_ids.append(x)

    g_to_x = []
    for s, _, d in g.in_edges(nbunch=x, data=True):
        if d[EDGE_TYPE] == GRANT:
            g_to_x.append(s)
    
    if g_to_x:
        visited = set()
        stack = [(v, x) for v in g_to_x]

        while stack:
            v, parent = stack.pop()
            if v not in visited:
                visited.add(v)
                if g.nodes[v][NODE_TYPE] == SUBJECT:
                    x_ids.append(v)
                for s, _, d in g.in_edges(nbunch=v, data=True):
                    if s != parent and d[EDGE_TYPE] == TAKE:
                        stack.append((s, v))

    if not x_ids:
        return False
    
    # condition 3.2
    

    return False


g, nodes_to_labels = read_graph('takegrant_example.json')
print_graph(g, nodes_to_labels)
# print(g.nodes.get('5932ee46-5bc5-47a2-b90c-ef713d61cec8'))
