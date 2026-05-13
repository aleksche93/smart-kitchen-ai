import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from core.memory import UserChefMemoryGraph, extract_and_store_traits

def test_memory_graph_operations():
    graph = UserChefMemoryGraph()
    graph.add_user_node("user_123", {"name": "Test User"})
    graph.add_chef_interaction("user_123", "scolded", {"reason": "pineapple on pizza"})
    
    assert "user_123" in graph.nodes
    assert len(graph.edges) == 1
    assert graph.edges[0]["source"] == "user_123"
    assert graph.edges[0]["target"] == "Chef"
    assert graph.edges[0]["relation"] == "scolded"

@pytest.mark.asyncio
async def test_extract_and_store_traits_exception_handling():
    # Mocking external calls to fail
    with patch("google.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("API Error"))
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}), \
             patch("core.memory.chroma_client", MagicMock()):
            # Should not raise exception, but log/print it
            await extract_and_store_traits("user message", "session_id")
            
            # Verification that it didn't crash is enough for "graceful failure" test
            assert True

@pytest.mark.asyncio
async def test_extract_and_store_traits_empty_input():
    # Should handle empty input gracefully
    with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}), \
         patch("core.memory.chroma_client", MagicMock()):
        with patch("google.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.aio.models.generate_content = AsyncMock(return_value=MagicMock(text='{}'))
            
            await extract_and_store_traits("", "session_id")
            assert True
