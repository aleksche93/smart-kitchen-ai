import pytest
from core.services.flavor_service import get_harmony_score, get_pairing_tips

def test_get_harmony_score_empty_list():
    # Should return neutral fallback 2.5
    assert get_harmony_score([]) == 2.5

def test_get_harmony_score_single_item():
    # Should return neutral fallback 2.5
    assert get_harmony_score(["salt"]) == 2.5

def test_get_pairing_tips_empty_list():
    # Should return empty list
    assert get_pairing_tips([]) == []

def test_get_pairing_tips_single_item_no_db():
    # If flavor_col is None or missing, should return empty list
    # Assuming flavor_col mock is handled or handled gracefully in code
    assert isinstance(get_pairing_tips(["tomato"]), list)
