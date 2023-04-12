import json
import uuid
import random

num_nodes = 30
num_edges = 75
node_types = ["TAKE", "GRANT", "A"]

node_labels = [f"node{i}" for i in range(1, num_nodes+1)]

nodes = [{"label": l, "id": l, "active": random.choice(["SUBJECT", "OBJECT"])} for l in node_labels]

edges = [{"id": str(uuid.uuid4()), "cclabel": random.choice(node_types),
          "source": random.choice(nodes)["id"],
          "target": random.choice(nodes)["id"]} for _ in range(num_edges)]

graph = {"graph": {"id": f"{num_nodes}_{num_edges}", "nodes": nodes, "edges": edges}}

with open(f"./test/random_graph_{num_nodes}_{num_edges}.json", "w") as f:
    json.dump(graph, f, indent=2)
