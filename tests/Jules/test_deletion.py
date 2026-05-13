import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_bulk_deletion_architecture():
    # Mock the SQLAlchemy async_session
    with patch('app.async_session') as mock_async_session:
        mock_session_instance = AsyncMock()
        # Ensure async with returns our mock session
        mock_async_session.return_value.__aenter__.return_value = mock_session_instance
        
        # Mock get receipt to return a dummy receipt object
        class DummyReceipt:
            image_path = None
        mock_session_instance.get.return_value = DummyReceipt()
        
        from app import delete_receipt_and_sync_inventory
        
        # Test 1: delete_items = True -> Should execute a bulk DELETE
        result = await delete_receipt_and_sync_inventory("123", delete_items=True)
        assert result is True
        
        # Check that session.execute was called for the bulk operation
        assert mock_session_instance.execute.call_count >= 1
        
        # Test 2: delete_items = False -> Should execute a bulk UPDATE (Set Null)
        mock_session_instance.execute.reset_mock()
        result = await delete_receipt_and_sync_inventory("123", delete_items=False)
        assert result is True
        
        # session.execute should be called with the bulk update statement
        assert mock_session_instance.execute.call_count >= 1
        
        # In both cases, session.commit() must be called
        assert mock_session_instance.commit.call_count == 2
