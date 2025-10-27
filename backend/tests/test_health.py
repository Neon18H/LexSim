"""Tests for the health endpoint."""
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_health_status_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
