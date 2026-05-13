import pytest
from unittest.mock import MagicMock
from core.fsm import ChefFSM, ChefState, ChefTrigger

@pytest.fixture
def mock_db():
    state_db = MagicMock()
    state_db.emotion_value = 0.0
    state_db.current_state = ChefState.IDLE.value
    state_db.personality_profile = "neutral"

    memory_db = MagicMock()
    memory_db.long_term_counters = {}

    session_db = MagicMock()
    session_db.recent_triggers = []

    return state_db, memory_db, session_db

@pytest.fixture
def fsm(mock_db):
    state_db, memory_db, session_db = mock_db
    return ChefFSM(state_db=state_db, memory_db=memory_db, session_db=session_db)

def test_determine_state_thresholds(fsm):
    assert fsm._determine_state(0.0) == ChefState.IDLE.value
    assert fsm._determine_state(-4.0) == ChefState.ACTIVE.value
    assert fsm._determine_state(-7.0) == ChefState.CREATIVE.value
    assert fsm._determine_state(5.0) == ChefState.ANNOYED.value
    assert fsm._determine_state(8.0) == ChefState.BOUNDARY.value
    assert fsm._determine_state(10.0) == ChefState.OFFLINE.value

def test_smooth_transition_logic(fsm):
    assert fsm._smooth_transition(ChefState.PLAYFUL.value, ChefState.SERIOUS.value) == ChefState.ACTIVE.value
    assert fsm._smooth_transition(ChefState.IDLE.value, ChefState.ACTIVE.value) == ChefState.ACTIVE.value

def test_update_state_by_trigger(fsm, mock_db):
    state_db, _, session_db = mock_db
    
    # triggering toxicity should increase emotion value towards anger
    initial_emotion = state_db.emotion_value
    state = fsm.trigger(ChefTrigger.TOXICITY)
    assert state_db.emotion_value > initial_emotion
