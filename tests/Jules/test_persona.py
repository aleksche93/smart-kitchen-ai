import pytest
from core.fsm import ChefFSM, ChefTrigger, ChefState
from core.persona import ChefPersona

# Lightweight mocks for DB models to ensure fast unit testing
class MockStateDB:
    def __init__(self):
        self.current_state = ChefState.IDLE.value
        self.emotion_value = 0.0
        self.personality_profile = "neutral"

class MockMemoryDB:
    def __init__(self):
        self.preferences = {}
        self.traits = {}
        self.cooking_sins = {}
        self.long_term_counters = {}

class MockSessionDB:
    def __init__(self):
        self.recent_triggers = []
        self.ui_events = []


def test_fsm_transitions():
    state_db = MockStateDB()
    memory_db = MockMemoryDB()
    session_db = MockSessionDB()
    
    fsm = ChefFSM(state_db=state_db, memory_db=memory_db, session_db=session_db)
    
    # Test triggering Toxicity to raise emotion and change state
    # IDLE -> depends on weights, TOXICITY gives +5. 
    # With neutral personality patience=1, annoyed_thresh = 4
    # So 5 >= 4, it should transition to ANNOYED
    new_state = fsm.trigger(ChefTrigger.TOXICITY)
    assert state_db.emotion_value > 0
    assert new_state == ChefState.ANNOYED.value
    
    # Respect should slowly lower the emotion level
    fsm.trigger(ChefTrigger.RESPECT)
    fsm.trigger(ChefTrigger.RESPECT)
    assert state_db.emotion_value < 5.0

def test_cooking_sins_accumulation():
    state_db = MockStateDB()
    memory_db = MockMemoryDB()
    session_db = MockSessionDB()
    
    fsm = ChefFSM(state_db=state_db, memory_db=memory_db, session_db=session_db)
    persona = ChefPersona(fsm=fsm)
    
    # Adding proteins
    persona.react_to_ingredient("chicken")
    # First protein should be fine
    assert "protein_chaos" not in memory_db.cooking_sins
    
    persona.react_to_ingredient("beef")
    # Second protein should still be fine
    assert "protein_chaos" not in memory_db.cooking_sins
    
    # Third protein -> chaos
    reaction = persona.react_to_ingredient("salmon")
    assert memory_db.cooking_sins.get("protein_chaos") is True
