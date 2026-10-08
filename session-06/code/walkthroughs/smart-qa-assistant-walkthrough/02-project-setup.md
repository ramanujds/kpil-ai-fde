# Step 2 — Project Setup

> Back to index · Previous: Concepts Overview · Next: Ingest the Documents

## Goal

Create the project folder, declare every dependency, and write the first version of
`config.py`, so that later steps have one place to read settings from.

## Why this matters

This project has two kinds of outside dependency: Python packages, and models running in
Ollama. Setting up both now means a failure later has one cause only, your code.

All settings live in one file, `config.py`. Two of them matter more than they look:

- **The embedding model.** Documents are turned into numbers when you ingest them, and
  questions are turned into numbers when someone asks. The two sets of numbers can only be
  compared if the **same model** made both. `config.py` sets one embedding model for the whole
  app, so ingest, search and the FAQ can never disagree.
- **`Settings.llm = None`.** LlamaIndex can also write replies, but here LangChain does all
  the talking. Turning LlamaIndex's model off means it can never quietly call a model you did
  not choose.

## 1. Create the Folder and `pyproject.toml`

```bash
mkdir smart-qa-assistant
cd smart-qa-assistant
```

Create `pyproject.toml`:

```toml
[project]
name = "smart-qa-assistant"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.5.9",
    "langchain>=1.4.3",
    "langchain-ollama>=1.1.0",
    "langgraph>=1.2.14",
    "llama-index-core>=0.14.25",
    "llama-index-embeddings-ollama>=0.10.0",
    "llama-index-vector-stores-chroma>=0.6.0",
    "numpy>=2.2.6",
    "python-dotenv>=1.2.4",
    "streamlit>=1.65.0",
]
```

All dependencies are listed now, including `streamlit` for Step 13, so you only sync once.

| Package | Used for |
|---|---|
| `langchain`, `langchain-ollama`, `langgraph` | The agent, the Ollama model, the memory and the approval pause |
| `llama-index-core`, `llama-index-embeddings-ollama` | Reading, splitting and searching documents; embeddings from Ollama |
| `chromadb`, `llama-index-vector-stores-chroma` | The vector store, and LlamaIndex's connection to it |
| `numpy` | A little maths for the FAQ matcher |
| `python-dotenv` | Reads `.env` |
| `streamlit` | The browser UI |

## 2. Create `.gitignore`

```text
.venv/
__pycache__/
.env
.chroma/
```

`.venv/` and `__pycache__/` are generated. `.chroma/` is the vector store you will build, which
can be rebuilt any time. `.env` holds your local settings.

## 3. Create `.env.example`

```text
# Local Ollama. No key needed. Change these only if your setup differs.
OLLAMA_BASE_URL=http://localhost:11434
CHAT_MODEL=llama3.1:8b
EMBED_MODEL=nomic-embed-text
```

This is the template. The defaults already work for a normal Ollama install, so you only need
a `.env` if yours is different:

```bash
cp .env.example .env
```

There is no key to protect here, which is one reason to run models locally. The `.env` habit
is still worth keeping, for the day you point this at a hosted model.

## 4. Build the Environment

```bash
uv sync
```

## 5. Write `config.py` (First Version)

Create `config.py`:

```python
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
```

`os.getenv("NAME", "default")` reads a setting from the environment, or uses the default.
`Settings` is LlamaIndex's global settings object: anything LlamaIndex does later will use the
embedding model set here. `config.py` has other lines to come; you will add them in later steps,
always at the end.

## Try it

```bash
uv run python -c "import config; print(config.CHAT_MODEL)"
```

```text
LLM is explicitly disabled. Using MockLLM.
llama3.1:8b
```

The first line is LlamaIndex confirming that `Settings.llm = None` worked. It is not an error,
and you will see it every time this project starts.

## Checkpoint

<details>
<summary>Full <code>config.py</code></summary>

```python
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
```

</details>

This is the first of five versions of `config.py`. It matches the reference file's first 21
lines. The other files, `pyproject.toml`, `.gitignore` and `.env.example`, match the reference
files exactly. Your `uv.lock` is created by `uv sync`, and its contents may differ slightly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `uv: command not found` | uv is not installed | Install uv, then reopen the terminal |
| `ModuleNotFoundError: llama_index` | You ran plain `python`, outside the environment | Use `uv run` |
| Connection errors to `localhost:11434` later | Ollama is not running | Start the Ollama app or run `ollama serve` |
| `config.py` changes seem ignored | You edited `.env.example` instead of `.env` | Settings are read from `.env`; the example file is only a template |

Next: **Step 3 — Ingest the Documents**.
