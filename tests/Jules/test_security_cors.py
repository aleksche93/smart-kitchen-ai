import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_cors_allowed_origin():
    """Verify that trusted origins are allowed."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

def test_cors_disallowed_origin():
    """Verify that wildcard origins and unknown domains are blocked."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.headers.get("access-control-allow-origin") != "http://evil.com"
    assert response.headers.get("access-control-allow-origin") != "*"
