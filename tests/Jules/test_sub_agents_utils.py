import pytest
from core.agents.sub_agents import _build_gemini_contents

def test_build_gemini_contents_basic():
    system_prompt = "You are a chef"
    chat_history = []
    user_input = "Hello"
    
    contents = _build_gemini_contents(system_prompt, chat_history, user_input)
    
    assert len(contents) == 3
    assert contents[0].role == "user"
    assert "You are a chef" in contents[0].parts[0].text
    
    assert contents[-1].role == "user"
    assert "Hello" in contents[-1].parts[0].text

def test_build_gemini_contents_with_history():
    system_prompt = "You are a chef"
    chat_history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "How can I help?"}
    ]
    user_input = "Tell me a recipe"
    
    contents = _build_gemini_contents(system_prompt, chat_history, user_input)
    
    # Check the system prompt and ACK
    assert contents[0].role == "user"
    assert "You are a chef" in contents[0].parts[0].text
    assert contents[1].role == "model"
    
    # Check chat history mapping
    assert contents[2].role == "user"
    assert "Hi" in contents[2].parts[0].text
    
    assert contents[3].role == "model"
    assert "How can I help?" in contents[3].parts[0].text
    
    # Check final user input
    assert contents[4].role == "user"
    assert "Tell me a recipe" in contents[4].parts[0].text
