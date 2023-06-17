import json
import uuid
import random
from utils import *


def generate_random_graphs():
    num_nodes = 30
    num_edges = 75
    node_types = ["TAKE", "GRANT", "A"]

    node_labels = [f"node{i}" for i in range(1, num_nodes+1)]

    nodes = [{"label": l, "id": l, "active": random.choice(
        ["SUBJECT", "OBJECT"])} for l in node_labels]

    edges = [{"id": str(uuid.uuid4()), "cclabel": random.choice(node_types),
              "source": random.choice(nodes)["id"],
              "target": random.choice(nodes)["id"]} for _ in range(num_edges)]

    graph = {"graph": {"id": f"{num_nodes}_{num_edges}",
                       "nodes": nodes, "edges": edges}}

    with open(f"./test/random_graph_{num_nodes}_{num_edges}.json", "w") as f:
        json.dump(graph, f, indent=2)


def generate_chain(input_graph: str, chain_length: int) -> str:
    output_graph = {
        "graph": {
            "label": f"chain_{chain_length}_" + input_graph["graph"]["label"],
            "nodes": [],
            "edges": []
        }
    }

    for i in range(chain_length):
        prefix = f"{i}_"
        for node in input_graph["graph"]["nodes"]:
            new_node = node.copy()
            new_node["label"] = new_node["id"] = prefix + new_node["id"]
            output_graph["graph"]["nodes"].append(new_node)

        for edge in input_graph["graph"]["edges"]:
            new_edge = edge.copy()
            new_edge["source"] = prefix + new_edge["source"]
            new_edge["target"] = prefix + new_edge["target"]
            new_edge["id"] = new_edge["source"] + new_edge["target"]
            output_graph["graph"]["edges"].append(new_edge)

        if i > 0:
            output_graph["graph"]["edges"].append({
                "id": f"{i - 1}_7{i}_1",
                "cclabel": "TAKE",
                "source": f"{i - 1}_7",
                "target": f"{i}_1"
            })

    return output_graph


graph_name = 'example3-complex-graph'
with open(f"./test/{graph_name}.json", "r") as f:
    input_graph = json.load(f)

chain_length = 86
output_graph = generate_chain(input_graph, chain_length)
with open(f"./test/chain_{chain_length}_{graph_name}.json", "w") as f:
    json.dump(output_graph, f, indent=2)
