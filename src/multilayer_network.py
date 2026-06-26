import json
import os
import networkx as nx
from config import NETWORK_PATH, DATA_DIR


class MultilayerNetwork:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_node(self, node_id: str, capa: str, **attrs):
        attrs["capa"] = capa
        self.graph.add_node(node_id, **attrs)

    def add_edge(self, arista):
        self.graph.add_edge(
            arista.source, arista.target,
            key=f"{arista.source}->{arista.target}",
            type=arista.type,
            layer_source=arista.layer_source,
            layer_target=arista.layer_target,
            weight=arista.weight,
            status=arista.status,
            human_review=arista.human_review,
        )

    def get_nodes_by_layer(self, capa: str):
        return [
            (n, d) for n, d in self.graph.nodes(data=True)
            if d.get("capa") == capa
        ]

    def to_supra_adjacency(self):
        layers = list(set(
            d.get("capa") for _, d in self.graph.nodes(data=True) if d.get("capa")
        ))
        matrix = {l1: {l2: [] for l2 in layers} for l1 in layers}
        for u, v, k, d in self.graph.edges(keys=True, data=True):
            ls = d.get("layer_source", "desconocida")
            lt = d.get("layer_target", "desconocida")
            if ls in matrix and lt in matrix[ls]:
                matrix[ls][lt].append({
                    "source": u, "target": v, "type": d.get("type"),
                    "weight": d.get("weight", 1),
                })
        return matrix

    def to_dict(self):
        nodes_data = []
        for n, d in self.graph.nodes(data=True):
            node = {"id": n}
            node.update({k: v for k, v in d.items() if v is not None})
            nodes_data.append(node)

        edges_data = []
        for u, v, k, d in self.graph.edges(keys=True, data=True):
            edge = {"source": u, "target": v}
            edge.update({k2: v2 for k2, v2 in d.items() if v2 is not None})
            edges_data.append(edge)

        return {"nodes": nodes_data, "edges": edges_data}

    def save(self):
        data = self.to_dict()
        with open(NETWORK_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        try:
            graphml_path = os.path.join(DATA_DIR, "multilayer_network.graphml")
            nx.write_graphml(self.graph, graphml_path, encoding="utf-8")
        except Exception:
            pass

    def get_summary(self):
        layers = {}
        for n, d in self.graph.nodes(data=True):
            capa = d.get("capa", "desconocida")
            layers[capa] = layers.get(capa, 0) + 1
        edge_types = {}
        for _, _, _, d in self.graph.edges(keys=True, data=True):
            t = d.get("type", "desconocida")
            edge_types[t] = edge_types.get(t, 0) + 1
        return {
            "total_nodos": self.graph.number_of_nodes(),
            "total_aristas": self.graph.number_of_edges(),
            "capas": layers,
            "tipos_relacion": edge_types,
        }
