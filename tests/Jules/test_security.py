import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app import app, DEFAULT_USER_ID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
import asyncio

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True, scope="module")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_save_ui_layout():
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

@pytest.mark.asyncio
async def test_save_ui_layout_idempotency():
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

@pytest.mark.asyncio
async def test_sql_injection_defense():
    """Verify that the layout save endpoint resists basic SQL injection via widget_id"""
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
