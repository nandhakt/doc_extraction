"""
Configuration settings for the Document Extraction Agent.

Environment Variables Required:
    - OPENAI_API_KEY: Your OpenAI API key
    - OPENAI_MODEL: Model to use (default: gpt-4o)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Server Configuration
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "localhost")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))

# Application Settings
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE_MB = 50

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


