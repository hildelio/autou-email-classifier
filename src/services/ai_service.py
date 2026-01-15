import json
import re

import google.generativeai as genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL


class AIService:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model or GEMINI_MODEL
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model_name)

    async def classify_email(self, email_content: str) -> dict:
        if not email_content or not email_content.strip():
            raise ValueError("Conteúdo do email não pode estar vazio")

        system_prompt = self._create_system_prompt()
        user_message = f"Classifique este email:\n\n{email_content}"

        try:
            response = self.client.generate_content(f"{system_prompt}\n\n{user_message}")

            # Extrair JSON da resposta
            result = self._parse_response(response.text)
            return result

        except Exception as e:
            raise RuntimeError(f"Erro ao classificar email com Gemini: {str(e)}") from e

    def _create_system_prompt(self) -> str:
        return """Você é um classificador de emails inteligente.
Analise o email fornecido e retorne um JSON com:
- category: Categoria do email (spam, importante, promoção, suporte, outro)
- confidence: Nível de confiança da classificação (0.0 a 1.0)
- suggested_reply: Sugestão de resposta breve (máximo 50 palavras)
- reasoning: Breve explicação da classificação

Retorne APENAS o JSON válido, sem markdown ou formatação adicional.
Exemplo de resposta esperada:
{"category": "importante", "confidence": 0.95, "suggested_reply": "Agradecemos seu contato...", "reasoning": "Email contém conteúdo crítico"}"""

    def _parse_response(self, response_text: str) -> dict:
        # Tentar extrair JSON da resposta
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)

        if not json_match:
            raise ValueError("Resposta do Gemini não contém JSON válido")

        try:
            result = json.loads(json_match.group())

            # Validar campos obrigatórios
            required_fields = ["category", "confidence", "suggested_reply"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Campo obrigatório ausente: {field}")

            # Validar tipos
            if not isinstance(result["category"], str):
                raise ValueError("'category' deve ser string")
            if not isinstance(result["confidence"], (int, float)):
                raise ValueError("'confidence' deve ser número")
            if not isinstance(result["suggested_reply"], str):
                raise ValueError("'suggested_reply' deve ser string")

            # Normalizar confiança para 0-1
            result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido na resposta: {str(e)}") from e
