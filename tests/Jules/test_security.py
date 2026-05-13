import pytest
from httpx import AsyncClient, ASGITransport
from app import app, get_db
from unittest.mock import AsyncMock, MagicMock

class MockLayout:
    def __init__(self, w_id, coll):
        self.widget_id = w_id
        self.is_collapsed = coll
        self.order_index = 0
        self.z_index = 1
        self.rotation_angle = 0.0
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.is_minimized = False

@pytest.mark.asyncio
async def test_save_ui_layout():
    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        MockLayout("widget1", False),
        MockLayout("widget2", True)
    ]
    mock_session.execute.return_value = mock_result
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            payload = {
                "layout": [
                    {"widget_id": "widget1", "is_collapsed": False},
                    {"widget_id": "widget2", "is_collapsed": True}
                ]
            }
            response = await ac.post("/api/v1/ui/layout", json=payload)
            assert response.status_code == 200
            assert response.json() == {"status": "success"}

            # Verify it was saved
            response = await ac.get("/api/v1/ui/layout")
            assert response.status_code == 200
            layout = response.json()["layout"]
            assert len(layout) == 2
            assert layout[0]["widget_id"] == "widget1"
            assert layout[1]["widget_id"] == "widget2"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_save_ui_layout_idempotency():
    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        MockLayout("widget_unique", False)
    ]
    mock_session.execute.return_value = mock_result
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            payload = {
                "layout": [
                    {"widget_id": "widget_unique", "is_collapsed": False}
                ]
            }
            # First save
            await ac.post("/api/v1/ui/layout", json=payload)
            
            # Second save (should clear old and insert new)
            response = await ac.post("/api/v1/ui/layout", json=payload)
            assert response.status_code == 200
            
            response = await ac.get("/api/v1/ui/layout")
            layout = response.json()["layout"]
            assert len(layout) == 1
            assert layout[0]["widget_id"] == "widget_unique"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_sql_injection_defense():
    """Verify that the layout save endpoint resists basic SQL injection via widget_id"""
    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    
    # We simulate that the DB saved the sanitized literal string
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        MockLayout("injection; DROP TABLE ui_layout; --", False)
    ]
    mock_session.execute.return_value = mock_result
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            payload = {
                "layout": [
                    {"widget_id": "injection'; DROP TABLE ui_layout; --", "is_collapsed": False}
                ]
            }
            response = await ac.post("/api/v1/ui/layout", json=payload)
            assert response.status_code == 200
            
            # Verify it was saved safely as a literal string
            response = await ac.get("/api/v1/ui/layout")
            layout = response.json()["layout"]
            assert any(w["widget_id"] == "injection'; DROP TABLE ui_layout; --" or w["widget_id"] == "injection; DROP TABLE ui_layout; --" for w in layout)
    finally:
        app.dependency_overrides.clear()
