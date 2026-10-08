"""
Configuration: the three settings every LLM call needs.

  LLM_BASE_URL  where the API lives (your laptop for Ollama, a cloud address for OpenAI)
  LLM_API_KEY   the secret that proves who you are (Ollama ignores it, OpenAI requires it)
  LLM_MODEL     which model should answer

They come from environment variables, so the SAME code runs against Ollama
or OpenAI just by changing values in the .env file. No key is ever written
inside a .py file, so nothing secret can end up in Git.
"""

import os

from dotenv import load_dotenv

# Reads a file named .env in this folder (if it exists) and puts each line
# into the environment. If there is no .env file, nothing happens.
load_dotenv()

# os.getenv(name, default): use the environment value, else the default.
# The defaults describe a local Ollama, so the examples work with no .env at all.
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("LLM_API_KEY", "ollama")
MODEL = os.getenv("LLM_MODEL", "llama3:8b")
