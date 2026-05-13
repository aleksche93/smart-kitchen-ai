import pytest
from core.agents.orchestrator import ChefOrchestrator

def test_tag_thought_basic():
    orchestrator = ChefOrchestrator()
    # Use a prefix from _UI_THOUGHT_PREFIXES
    event = {"type": "status", "data": {"text": "Chef is thinking about eggs..."}}
    
    tagged = orchestrator._tag_thought(event)
    
    assert tagged["data"].get("ui_thought") is True
    assert tagged["data"]["text"] == "Chef is thinking about eggs..."

def test_tag_thought_with_agent_name():
    orchestrator = ChefOrchestrator()
    event = {"type": "status", "data": {"text": "Analyzing flavors"}}
    
    tagged = orchestrator._tag_thought(event, agent_name="FlavorArchitect")
    
    # FlavorArchitect uses "The Mad Alchemist" persona
    assert "[The Mad Alchemist]" in tagged["data"]["text"]
    assert tagged["data"].get("ui_thought") is True

def test_tag_thought_already_seen():
    orchestrator = ChefOrchestrator()
    # Must use a prefix for it to even be considered a ui_thought
    event = {"type": "status", "data": {"text": "Chef is doing something repetitive"}}
    seen = {"Chef is doing something repetitive"}
    
    tagged = orchestrator._tag_thought(event, seen_thoughts=seen)
    
    # If it's in seen_thoughts, it's returned unmodified (no ui_thought key added)
    assert "ui_thought" not in tagged["data"]

def test_tag_thought_non_status_event():
    orchestrator = ChefOrchestrator()
    event = {"type": "delta", "data": {"text": "Some content"}}
    
    tagged = orchestrator._tag_thought(event)
    
    assert "ui_thought" not in tagged["data"]
