"""
LLM Client Utility

WHY THIS FILE?
- Provides a reusable way to interact with the LLM (GPT-4o)
- Handles SSL issues with corporate networks (like in testing.py)
- Creates embeddings for RAG (Retrieval Augmented Generation)

WHAT IT DOES:
- Initializes ChatOpenAI client with proper SSL handling
- Provides function to generate embeddings for text
- Used by all agents to communicate with AI models
"""

import httpx
import requests
import numpy as np
from langchain_openai import ChatOpenAI
from backend.config import (
    GENAI_API_KEY,
    GENAI_BASE_URL,
    GENAI_LLM_MODEL,
    GENAI_EMBEDDING_MODEL
)

# Disable SSL warnings for corporate networks
# In production, you'd use proper SSL certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# HTTP CLIENT SETUP
# =========================
# WHY? Corporate networks often have SSL certificate issues
# verify=False bypasses SSL verification (use cautiously!)
http_client = httpx.Client(verify=False)

# =========================
# LLM CLIENT (ChatGPT-4o)
# =========================
# WHY? This is the "brain" of our AI system
# It generates intelligent responses, plans itineraries, and reasons about travel
llm = ChatOpenAI(
    base_url=GENAI_BASE_URL,
    model=GENAI_LLM_MODEL,
    api_key=GENAI_API_KEY,
    http_client=http_client,
    temperature=0.7,  # Controls creativity (0=deterministic, 1=very creative)
)

# =========================
# EMBEDDING FUNCTION
# =========================
def get_embedding(text: str) -> list:
    """
    Convert text into a numerical vector (embedding)
    
    WHY EMBEDDINGS?
    - Embeddings capture semantic meaning of text
    - Similar texts have similar embeddings
    - Enables semantic search in vector database
    
    EXAMPLE:
    "Luxury Mars hotel" and "Premium Martian accommodation"
    will have very similar embeddings even though words differ
    
    Args:
        text: The text to convert to embedding
        
    Returns:
        List of floats representing the embedding vector (3072 dimensions)
    """
    url = f"{GENAI_BASE_URL}/embeddings"
    
    headers = {
        "Authorization": f"Bearer {GENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GENAI_EMBEDDING_MODEL,
        "input": text
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=False  # SSL bypass for corporate network
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract the embedding vector from API response
        return data["data"][0]["embedding"]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Embedding API Error: {str(e)}")
        raise

# =========================
# COSINE SIMILARITY
# =========================
def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """
    Calculate similarity between two embedding vectors
    
    WHY?
    - Measures how similar two pieces of text are
    - Returns value between -1 (opposite) and 1 (identical)
    - Used to rank search results by relevance
    
    EXAMPLE:
    similarity("Mars hotel", "Martian accommodation") = 0.92 (very similar)
    similarity("Mars hotel", "Lunar crater") = 0.45 (somewhat related)
    
    Args:
        vec_a: First embedding vector
        vec_b: Second embedding vector
        
    Returns:
        Similarity score between -1 and 1
    """
    a = np.array(vec_a)
    b = np.array(vec_b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("LLM Client initialized successfully!")
