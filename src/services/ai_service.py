"""
AI Service - Para integração com Google Gemini
"""


import google.generativeai as genai


class AIService:
    """Serviço de integração com Google Gemini Pro"""

    def __init__(self, api_key: str):
        """
        Inicializar serviço de IA

        Args:
            api_key: Chave de API do Google Gemini
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

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
