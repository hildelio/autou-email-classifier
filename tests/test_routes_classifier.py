"""
Tests for Classifier Routes
"""

import io
import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

# Configurar variáveis de ambiente ANTES de imports
os.environ.setdefault("GEMINI_API_KEY", "test-key-12345")
os.environ.setdefault("GEMINI_MODEL", "gemini-2.5-flash")

# noqa: E402 - imports após setdefault é intencional
from src.main import app  # noqa: E402

client = TestClient(app)


class TestClassifierRoutes:
    """Test cases for classifier routes"""

    def test_analyze_endpoint_exists(self):
        """Test that /api/analyze endpoint exists"""
        response = client.post("/api/analyze")
        # Vai falhar porque não tem arquivo, mas não 404
        assert response.status_code != 404

    def test_analyze_without_file(self):
        """Test /api/analyze without file"""
        response = client.post("/api/analyze")
        assert response.status_code == 422  # Unprocessable entity

    def test_analyze_with_invalid_file_type(self):
        """Test /api/analyze with invalid file type"""
        file_content = b"some content"
        files = {
            "file": (
                "test.docx",
                io.BytesIO(file_content),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        }
        response = client.post("/api/analyze", files=files)
        assert response.status_code == 400
        assert "não suportado" in response.json()["detail"]

    def test_analyze_with_txt_file(self):
        """Test /api/analyze with valid TXT file"""
        file_content = b"Este eh um email de teste para classificacao."
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

        with patch(
            "src.services.ai_service.AIService.classify_email",
            new_callable=AsyncMock,
        ) as mock_classify:
            mock_classify.return_value = {
                "category": "importante",
                "confidence": 0.95,
                "suggested_reply": "Obrigado pelo contato",
                "reasoning": "Email contém conteúdo importante",
            }

            response = client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()
            assert data["category"] == "importante"
            assert data["confidence"] == 0.95
            assert "Obrigado" in data["suggested_reply"]

    def test_analyze_response_model(self):
        """Test that response follows ClassificationResponse model"""
        file_content = b"Email de teste"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

        with patch(
            "src.services.ai_service.AIService.classify_email",
            new_callable=AsyncMock,
        ) as mock_classify:
            mock_classify.return_value = {
                "category": "spam",
                "confidence": 0.87,
                "suggested_reply": "Deletar",
                "reasoning": "Padrão de spam detectado",
            }

            response = client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()

            # Validar estrutura
            assert "category" in data
            assert "confidence" in data
            assert "suggested_reply" in data
            assert isinstance(data["confidence"], float)
            assert 0.0 <= data["confidence"] <= 1.0

    def test_analyze_empty_file(self):
        """Test /api/analyze with empty file"""
        file_content = b""
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

        response = client.post("/api/analyze", files=files)

        assert response.status_code == 400
        assert "vazio" in response.json()["detail"]

    def test_analyze_api_error_handling(self):
        """Test error handling when API fails"""
        file_content = b"Test email content"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

        with patch(
            "src.services.ai_service.AIService.classify_email",
            new_callable=AsyncMock,
        ) as mock_classify:
            mock_classify.side_effect = RuntimeError("API Error")

            response = client.post("/api/analyze", files=files)

            assert response.status_code == 500
            assert "API Error" in response.json()["detail"]
