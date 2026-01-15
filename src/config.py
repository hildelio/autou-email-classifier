"""
Configuration Management - Simple and Straightforward
"""

from os import getenv

# Application Settings
APP_NAME = "Autou Email Classifier"
APP_VERSION = "0.1.0"
ENVIRONMENT = getenv("ENVIRONMENT", "development")
DEBUG = getenv("DEBUG", "true").lower() == "true"

# AI Model Configuration
GEMINI_API_KEY = getenv("GEMINI_API_KEY")
GEMINI_MODEL = getenv("GEMINI_MODEL")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

if not GEMINI_MODEL:
    raise ValueError("GEMINI_MODEL environment variable is required")

