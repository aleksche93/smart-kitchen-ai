import pytest
from core.graph_manager import UserChefMemoryGraph

def test_graph_memory_lifecycle():
    # 1. Initialize graph
    graph = UserChefMemoryGraph()
    
    # 2. Add nodes/edges
    graph.add_node("UserPreference", "User", {"name": "TestUser"})
    graph.add_node("Ingredient", "Garlic", {"category": "Vegetable"})
    graph.add_edge("User", "Garlic", "DISLIKES")
    
    # 3. Serialize to JSON
    graph_data = graph.serialize()
    
    assert "nodes" in graph_data
    assert "edges" in graph_data
    
    # 4. Deserialize from JSON
    new_graph = UserChefMemoryGraph()
    new_graph.deserialize(graph_data)
    
    # 5. Assert graph integrity
    assert new_graph.graph.has_node("User")
    assert new_graph.graph.has_node("Garlic")
    assert new_graph.graph.has_edge("User", "Garlic")
    
    # Check attributes
    user_attrs = new_graph.graph.nodes["User"]
    assert user_attrs["type"] == "UserPreference"
    assert user_attrs["name"] == "TestUser"
    
    edge_attrs = new_graph.graph.edges["User", "Garlic"]
    assert edge_attrs["relationship"] == "DISLIKES"
