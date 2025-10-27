"""Tests for the FastAPI application."""
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "service" in payload


def test_simulate_endpoint_returns_structure():
    payload = {"prompt": "alpha beta gamma"}
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prompt"] == payload["prompt"].strip()
    assert isinstance(data["steps"], list)
    assert data["steps"], "Expected at least one step"
    assert "summary" in data
    assert "metadata" in data


def test_simulate_rejects_empty_prompt():
    response = client.post("/api/simulate", json={"prompt": "   "})
    assert response.status_code == 422
