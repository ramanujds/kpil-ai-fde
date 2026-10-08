"""Settings shared by every file, read from .env (see .env.example).

Both models run locally in Ollama, so no API key is needed.
"""

import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.1:8b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# One embedding model for the whole app. ingest.py, rag.py and faq.py must all use the
# same one, or the vectors cannot be compared. If you change it, run ingest.py again.
Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
Settings.llm = None  # LlamaIndex only retrieves here. LangChain does all the talking.

# Where the vectors live: a Chroma database on disk, in this folder.
CHROMA_PATH = ".chroma"
COLLECTION = "company_docs"

# Retrieval settings.
TOP_K = 3  # passages handed to the model
MIN_SCORE = 0.65  # passages scoring below this are dropped (weak match = "not found")
FAQ_MIN_SCORE = 0.85  # FAQ needs a much closer match than RAG, so near-misses fall through

# The signed-in employee. Real systems get this from single sign-on, never from the chat.
CURRENT_USER = "E102"
