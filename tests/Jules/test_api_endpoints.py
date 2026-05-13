import pytest
from httpx import AsyncClient, ASGITransport
from app import app, get_db
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

@pytest.mark.asyncio
async def test_clear_session_no_session():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Clear session is POST
            response = await ac.post("/api/v1/chef/session/clear")
            assert response.status_code == 200
            assert response.json()["status"] == "success"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_receipt_db_error_handling():
    # Test an endpoint that actually calls session.rollback() on error
    # POST /api/v1/fridge/receipt rolls back on error.
    mock_session = AsyncMock()
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result
    
    mock_session.commit.side_effect = SQLAlchemyError("Commit failed")
    app.dependency_overrides[get_db] = lambda: mock_session
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            files = {'file': ('test.jpg', b'fake image data', 'image/jpeg')}
            
            with patch("app.client") as mock_client:
                # Mock the genai client response so it reaches commit
                mock_client.aio.models.generate_content.return_value.parsed = None
                mock_client.aio.models.generate_content.return_value.text = '{"store_name": "Test", "items": []}'
                
                response = await ac.post("/api/v1/fridge/receipt", files=files)
                
                assert response.status_code == 500
                mock_session.rollback.assert_awaited()
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_parse_receipt_vision_invalid_file():
    mock_session = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            files = {'file': ('test.txt', b'not an image', 'text/plain')}
            response = await ac.post("/api/v1/fridge/receipt", files=files)
            assert response.status_code == 400
            assert "Only JPG, PNG, or WEBP allowed" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
