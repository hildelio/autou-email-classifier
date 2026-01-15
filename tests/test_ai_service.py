"""
Tests for AIService
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.services.ai_service import AIService

# Configurar variáveis de ambiente para testes
os.environ["GEMINI_API_KEY"] = "test-key-12345"
os.environ["GEMINI_MODEL"] = "gemini-2.5-flash"


class TestAIService:
    """Test cases for AIService"""

    @pytest.fixture
    def ai_service(self):
        """Create AIService instance for testing"""
        return AIService(api_key="test-key-12345", model="gemini-2.5-flash")

    def test_init_with_custom_params(self):
        """Test AIService initialization with custom parameters"""
        service = AIService(api_key="custom-key", model="custom-model")
        assert service.api_key == "custom-key"
        assert service.model_name == "custom-model"

    def test_init_from_config(self):
        """Test AIService initialization from config"""
        service = AIService()
        assert service.api_key is not None
        assert service.model_name is not None

    def test_create_system_prompt(self, ai_service):
        """Test system prompt creation"""
        prompt = ai_service._create_system_prompt()
        assert isinstance(prompt, str)
        assert "JSON" in prompt
        assert "categoria" in prompt.lower() or "category" in prompt

    def test_parse_response_valid_json(self, ai_service):
        """Test parsing valid JSON response"""
        response_text = '{"category": "importante", "confidence": 0.95, "suggested_reply": "Resposta", "reasoning": "Motivo"}'
        result = ai_service._parse_response(response_text)

        assert result["category"] == "importante"
        assert result["confidence"] == 0.95
        assert result["suggested_reply"] == "Resposta"

    def test_parse_response_json_with_markdown(self, ai_service):
        """Test parsing JSON response wrapped in markdown"""
        response_text = """```json
        {"category": "spam", "confidence": 0.87, "suggested_reply": "Deletar", "reasoning": "Suspicious"}
        ```"""
        result = ai_service._parse_response(response_text)

        assert result["category"] == "spam"
        assert result["confidence"] == 0.87

    def test_parse_response_missing_field(self, ai_service):
        """Test error when required field is missing"""
        response_text = '{"category": "importante", "confidence": 0.95}'
        with pytest.raises(ValueError, match="Campo obrigatório ausente"):
            ai_service._parse_response(response_text)

    def test_parse_response_invalid_json(self, ai_service):
        """Test error for invalid JSON"""
        response_text = "This is not JSON at all"
        with pytest.raises(ValueError, match="não contém JSON"):
            ai_service._parse_response(response_text)

    def test_parse_response_confidence_normalization(self, ai_service):
        """Test confidence normalization to 0-1 range"""
        # Test value > 1
        response_text = '{"category": "importante", "confidence": 1.5, "suggested_reply": "Teste", "reasoning": "X"}'
        result = ai_service._parse_response(response_text)
        assert result["confidence"] == 1.0

        # Test value < 0
        response_text = '{"category": "importante", "confidence": -0.5, "suggested_reply": "Teste", "reasoning": "X"}'
        result = ai_service._parse_response(response_text)
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_classify_email_empty_content(self, ai_service):
        """Test error when email content is empty"""
        with pytest.raises(ValueError, match="não pode estar vazio"):
            await ai_service.classify_email("")

    @pytest.mark.asyncio
    async def test_classify_email_whitespace_only(self, ai_service):
        """Test error when email content is whitespace only"""
        with pytest.raises(ValueError, match="não pode estar vazio"):
            await ai_service.classify_email("   \n  \t  ")

    @pytest.mark.asyncio
    async def test_classify_email_success(self, ai_service):
        """Test successful email classification"""
        mock_response = MagicMock()
        mock_response.text = '{"category": "importante", "confidence": 0.92, "suggested_reply": "Obrigado", "reasoning": "Crítico"}'

        with patch.object(ai_service.client, "generate_content", return_value=mock_response):
            result = await ai_service.classify_email("Test email content")

            assert result["category"] == "importante"
            assert result["confidence"] == 0.92
            assert "Obrigado" in result["suggested_reply"]

    @pytest.mark.asyncio
    async def test_classify_email_api_error(self, ai_service):
        """Test handling of API errors"""
        with patch.object(
            ai_service.client,
            "generate_content",
            side_effect=Exception("API Error"),
        ):
            with pytest.raises(RuntimeError, match="Erro ao classificar"):
                await ai_service.classify_email("Test email")

    def test_parse_response_type_validation(self, ai_service):
        """Test type validation in response parsing"""
        # Invalid category type
        response_text = (
            '{"category": 123, "confidence": 0.95, "suggested_reply": "Teste", "reasoning": "X"}'
        )
        with pytest.raises(ValueError, match="deve ser string"):
            ai_service._parse_response(response_text)

        # Invalid confidence type
        response_text = '{"category": "importante", "confidence": "alto", "suggested_reply": "Teste", "reasoning": "X"}'
        with pytest.raises(ValueError, match="deve ser número"):
            ai_service._parse_response(response_text)
