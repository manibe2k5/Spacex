from langchain_openai import ChatOpenAI
import httpx
import requests
import certifi
import numpy as np

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# CONFIG
# =========================
api_key = "sk-fRY81_DXaoDSKSNg3dgxew"

BASE_URL = "https://genailab.tcs.in/v1"
EMBEDDING_MODEL = "azure/genailab-maas-text-embedding-3-large"

# =========================
# HTTP CLIENT (fix SSL if possible)
# =========================
# Try this first:
client = httpx.Client(verify=False)

# If your corporate network breaks SSL, uncomment this instead:
# client = httpx.Client(verify=False)

# =========================
# LLM (LangChain)
# =========================
llm = ChatOpenAI(
    base_url=BASE_URL,
    model="genailab-maas-gpt-35-turbo",
    api_key=api_key,
    http_client=client
)

# =========================
# EMBEDDING FUNCTION (Direct API)
# =========================
def get_embedding(text):
    url = f"{BASE_URL}/embeddings"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=False  # change to certifi.where() if SSL works
        )

        response.raise_for_status()
        data = response.json()

        return data["data"][0]["embedding"]

    except requests.exceptions.RequestException as e:
        print("❌ Embedding API Error:", str(e))
        raise

# =========================
# COSINE SIMILARITY
# =========================
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# =========================
# TEST LLM
# =========================
print("=== LLM RESPONSE ===")
print(llm.invoke("Tell me about yourself").content)

# =========================
# TEST EMBEDDINGS
# =========================
text1 = "LangChain helps build applications with LLMs."
text2 = "LangChain is a framework for developing language model applications."

print("\n=== GENERATING EMBEDDINGS ===")

embedding1 = get_embedding(text1)
embedding2 = get_embedding(text2)

# =========================
# SIMILARITY
# =========================
similarity = cosine_similarity(embedding1, embedding2)

print("\n=== RESULT ===")
print(f"Cosine Similarity: {similarity:.4f}")