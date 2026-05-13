import pytest
import os
import json
from unittest.mock import patch, mock_open
from core.locales import I18n

def test_i18n_load_translations():
    mock_data = {"test": {"key": "value"}}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        i18n = I18n(lang="en")
        assert i18n.translations == mock_data

def test_i18n_get_simple_key():
    mock_data = {"welcome": "Hello"}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        i18n = I18n(lang="en")
        assert i18n.get("welcome") == "Hello"

def test_i18n_get_nested_key():
    mock_data = {"chef": {"greet": "Hi"}}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        i18n = I18n(lang="en")
        assert i18n.get("chef.greet") == "Hi"

def test_i18n_get_fallback():
    mock_data = {"test": "val"}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        i18n = I18n(lang="en")
        assert i18n.get("missing.key", "Fallback") == "Fallback"

def test_i18n_load_error_handling():
    with patch("builtins.open", side_effect=Exception("Read Error")):
        i18n = I18n(lang="en")
        assert i18n.translations == {}
        assert i18n.get("any") == ""
