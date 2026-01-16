"""
Configuration Management - Simple and Straightforward
"""

from os import getenv

from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Application Settings
APP_NAME = "Autou Email Classifier"
APP_VERSION = "0.1.0"
ENVIRONMENT = getenv("ENVIRONMENT", "development")
DEBUG = getenv("DEBUG", "true").lower() == "true"

# AI Model Configuration
GEMINI_API_KEY = getenv("GEMINI_API_KEY")
GEMINI_MODEL = getenv("GEMINI_MODEL", "gemini-2.5-flash")

# OCR Configuration (opcional - apenas para PDFs escaneados)
OCR_SPACE_API_KEY = getenv("OCR_SPACE_API_KEY")

# Validar configuração crítica apenas em produção
if ENVIRONMENT == "production":
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    if not GEMINI_MODEL:
        raise ValueError("GEMINI_MODEL environment variable is required")
