"""
AI Service - Para integração com Google Gemini
"""

import google.generativeai as genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL


class AIService:
    """Serviço de integração com Google Gemini Pro"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Inicializar serviço de IA

        Args:
            api_key: Chave de API do Google Gemini (usa GEMINI_API_KEY se None)
            model: Modelo a usar (usa GEMINI_MODEL se None)
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model or GEMINI_MODEL
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    async def classify_email(self, email_content: str) -> dict:
        """
        Classificar email usando IA

        Args:
            email_content: Conteúdo do email para classificar

        Returns:
            Dicionário com categoria e resposta
        """
        # TODO: Implementar lógica de classificação
        pass

    def _create_system_prompt(self) -> str:
        """Criar prompt do sistema"""
        # TODO: Implementar prompt engineering
        pass
