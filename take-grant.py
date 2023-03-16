import json
from matplotlib import pyplot as plt
import networkx as nx

json_graph = json.load(open('takegrant_example.json', 'r'))
nodes = json_graph['graph']['nodes']
edges = json_graph['graph']['edges']

g = nx.DiGraph()

id_attrs = []
for node in nodes:
    id_attrs.append((node['id'], node))
g.add_nodes_from(id_attrs)

id_attrs.clear()
for edge in edges:
    id_attrs.append((edge['source'], edge['target'], edge))    
g.add_edges_from(id_attrs)

plot = plt.subplot(111)
nx.draw(g)
plt.savefig('graph_view')

