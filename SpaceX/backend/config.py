"""
Configuration Module for Stellar Voyage AI

WHY THIS FILE?
- Centralizes all configuration in one place
- Loads API keys securely from .env file (never hardcode secrets!)
- Makes it easy to change settings without touching code

WHAT IT DOES:
- Reads environment variables using python-dotenv
- Provides easy access to API credentials throughout the app
- Validates that required variables exist
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This reads the .env file and makes variables available via os.getenv()
load_dotenv()

# API Configuration
# These are loaded from .env file for security
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
GENAI_BASE_URL = os.getenv("GENAI_BASE_URL")
GENAI_LLM_MODEL = os.getenv("GENAI_LLM_MODEL")
GENAI_EMBEDDING_MODEL = os.getenv("GENAI_EMBEDDING_MODEL")

# Validate that all required environment variables are present
# This prevents cryptic errors later if .env is misconfigured
if not all([GENAI_API_KEY, GENAI_BASE_URL, GENAI_LLM_MODEL, GENAI_EMBEDDING_MODEL]):
    raise ValueError(
        "Missing required environment variables. "
        "Please check your .env file contains: "
        "GENAI_API_KEY, GENAI_BASE_URL, GENAI_LLM_MODEL, GENAI_EMBEDDING_MODEL"
    )

# NASA API Key for space weather (DONKI solar flares)
# Free key: https://api.nasa.gov  |  Falls back to DEMO_KEY if not set
NASA_API_KEY = os.getenv("NASA_API_KEY")  # Optional — DEMO_KEY works with rate limits

# Database paths
CHROMA_DB_PATH = "./chroma_db"  # Vector database storage location
SQLITE_DB_PATH = "./backend/data/stellar_voyage.db"  # Structured data storage

# Application settings
MAX_RETRIEVAL_RESULTS = 5  # How many similar documents to retrieve from vector DB
EMBEDDING_DIMENSION = 3072  # Azure text-embedding-3-large produces 3072-dimensional vectors

print("Configuration loaded successfully!")
print(f"Using LLM: {GENAI_LLM_MODEL}")
print(f"Using Embedding Model: {GENAI_EMBEDDING_MODEL}")
