"""
Testes básicos da API
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Fixture para cliente de testes"""
    return TestClient(app)


def test_health_check(client):
    """Teste do endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Teste do endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
