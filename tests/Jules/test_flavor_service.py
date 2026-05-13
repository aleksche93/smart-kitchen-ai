import pytest
from unittest.mock import patch, MagicMock
from core.services.flavor_service import get_harmony_score, get_pairing_tips

@patch('core.services.flavor_service.flavor_col')
def test_get_harmony_score_happy_path(mock_flavor_col):
    """Test harmony score calculation with successful ChromaDB response."""
    mock_results = {
        'documents': [
            ["Item pairs well with basil", "Item pairs well with garlic"],
            ["Item pairs well with tomato", "Item pairs well with onion"]
        ],
        'distances': [[0.1, 0.2], [0.15, 0.25]]
    }
    mock_flavor_col.query.return_value = mock_results
    
    score = get_harmony_score(["tomato", "basil"])
    assert 1.0 <= score <= 4.0

@patch('core.services.flavor_service.flavor_col')
def test_get_harmony_score_exception(mock_flavor_col):
    """Test harmony score calculation when ChromaDB fails."""
    mock_flavor_col.query.side_effect = Exception("ChromaDB Error")
    
    score = get_harmony_score(["tomato", "basil"])
    assert score == 2.5  # Expected neutral fallback

@patch('core.services.flavor_service.flavor_col')
def test_get_pairing_tips_happy_path(mock_flavor_col):
    """Test pairing tips with successful ChromaDB response."""
    mock_results = {
        'documents': [
            ["Item pairs well with garlic", "Item pairs well with onion"]
        ]
    }
    mock_flavor_col.query.return_value = mock_results
    
    tips = get_pairing_tips(["tomato"])
    assert isinstance(tips, list)
    assert len(tips) > 0

@patch('core.services.flavor_service.flavor_col')
def test_get_pairing_tips_exception(mock_flavor_col):
    """Test pairing tips when ChromaDB fails."""
    mock_flavor_col.query.side_effect = Exception("ChromaDB Error")
    
    tips = get_pairing_tips(["tomato"])
    assert tips == []
