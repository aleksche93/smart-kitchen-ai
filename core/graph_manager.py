import os
import json
from typing import Dict, Any

# Ensure GPU Acceleration via cuGraph is enabled before importing NetworkX
os.environ["NX_CUGRAPH_AUTOCONFIG"] = "True"
import networkx as nx

class UserChefMemoryGraph:
    """
    Native Graph Memory system using NetworkX.
    Nodes use strict dictionaries to prevent Prototype Pollution.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_type: str, node_id: str, attributes: Dict[str, Any]):
        """
        Adds a node to the graph.
        """
        safe_attributes = dict(attributes)
        safe_attributes["type"] = node_type
        self.graph.add_node(node_id, **safe_attributes)

    def add_edge(self, node_id_1: str, node_id_2: str, relationship: str):
        """
        Adds a directed edge between two nodes.
        """
        self.graph.add_edge(node_id_1, node_id_2, relationship=relationship)

    def serialize(self) -> Dict[str, Any]:
        """
        Serializes the graph to a JSON-compatible dictionary.
        """
        return nx.node_link_data(self.graph)

    def deserialize(self, graph_data: Dict[str, Any]):
        """
        Loads the graph from a JSON dictionary.
        """
        if graph_data:
            self.graph = nx.node_link_graph(graph_data)
        else:
            self.graph = nx.DiGraph()
