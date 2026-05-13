import pytest
from unittest.mock import MagicMock
from core.persona import ChefPersona
from core.fsm import ChefFSM, ChefState

@pytest.fixture
def mock_fsm():
    fsm = MagicMock(spec=ChefFSM)
    fsm.state_db = MagicMock()
    fsm.state_db.current_state = ChefState.IDLE.value
    fsm.memory_db = MagicMock()
    fsm.memory_db.preferences = {}
    fsm.memory_db.cooking_sins = {}
    fsm.session_db = MagicMock()
    fsm.session_db.ui_events = []
    return fsm

@pytest.fixture
def persona(mock_fsm):
    return ChefPersona(fsm=mock_fsm)

def test_update_preferences_spicy(persona, mock_fsm):
    persona.update_preferences("chili pepper")
    assert mock_fsm.memory_db.preferences["likes_spicy"] is True

def test_update_preferences_chicken(persona, mock_fsm):
    persona.update_preferences("roast chicken")
    assert mock_fsm.memory_db.preferences["likes_chicken"] is True

from unittest.mock import MagicMock, patch

def test_react_to_ingredient_fallback(persona):
    with patch("core.persona.i18n.get", return_value="Interesting."):
        reaction = persona.react_to_ingredient("mysterious substance")
        assert reaction == "Interesting."

def test_generate_system_prompt(persona):
    prompt = persona.generate_system_prompt()
    assert "IDLE" in prompt
    assert "Chaotic Genius" in prompt
    assert len(prompt) > 50
