# AI and Python: Calling an LLM

Small runnable examples that call a language model from Python. The same code works with a local model (Ollama) or a hosted one (OpenAI) because both offer the same "chat completions" API. Only three settings change.

Part of Day 3, Block 2 (API Calls and Authentication). The explanation lives in the notes folder `session-03/ai-and-python/`.

## Files

| File | What it does |
|---|---|
| `config.py` | Loads `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_MODEL` from the environment or a `.env` file. Defaults point at local Ollama. |
| `01_raw_http_call.py` | Calls the model with a plain HTTP request and prints the request body, the full JSON reply, the answer, the finish reason and token usage. Shows what really travels over the wire. |
| `02_sdk_call.py` | Makes the same call with the OpenAI Python SDK, using system and user roles, temperature and max tokens. Then sends a follow-up to show that the whole chat history is re-sent every time. |
| `.env.example` | Template for your settings. Copy it to `.env`. |
| `pyproject.toml` and `uv.lock` | The project's dependencies (`openai`, `httpx`, `python-dotenv`) and their pinned versions. |
| `.python-version` | The Python version uv uses (3.12). The code needs Python 3.10 or newer. |
| `.gitignore` | Keeps `.venv/`, `__pycache__/` and `.env` out of Git. |

## Prerequisites

1. **uv**, the Python package manager. Check with `uv --version`.
2. **A model to call**, either:
   - **Ollama** (free, runs on your machine): install it, then download a model once with `ollama pull llama3:8b`. Make sure Ollama is running.
   - **OpenAI** (or another OpenAI-compatible provider): an account and an API key.

## Setup

From this folder:

```
uv sync
```

This creates `.venv/` and installs the exact versions in `uv.lock`. There is nothing to activate; `uv run` always uses the right environment.

## Environment Variables

| Variable | Meaning | Default when not set |
|---|---|---|
| `LLM_BASE_URL` | Where the API lives | `http://localhost:11434/v1` (Ollama) |
| `LLM_API_KEY` | The secret key. Ollama ignores it, so any text works. | `ollama` |
| `LLM_MODEL` | Which model should answer | `llama3:8b` |

**Using Ollama with the defaults:** you do not need a `.env` file at all. Just run the examples.

**To change any setting**, copy the template and edit the copy:

```
cp .env.example .env
```

On Windows PowerShell use `Copy-Item .env.example .env`. Then open `.env` and edit the values.

**To use OpenAI**, put these in `.env` (the template has them commented out):

```
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-real-key
LLM_MODEL=gpt-4o-mini
```

You can also set a variable for a single run without touching `.env`. On macOS or Linux:

```
LLM_MODEL=mistral uv run python 02_sdk_call.py
```

## Run

```
uv run python 01_raw_http_call.py
uv run python 02_sdk_call.py
```

Read them in order. The first shows the raw request and response; the second does the same job with less code.

## Troubleshooting

| Message or symptom | Likely cause | Fix |
|---|---|---|
| Could not connect to the base URL | Ollama is not running, or the URL is wrong | Start Ollama and check `LLM_BASE_URL` |
| Model not found (404) | The model name is wrong or not downloaded | Run `ollama pull <model>`, or fix `LLM_MODEL` |
| API key was rejected (401) | Wrong or missing key for a hosted provider | Check `LLM_API_KEY` in `.env` |
| Too many requests (429) | You hit a rate limit | Wait a little and try again |
| The first answer is very slow | A local model is loading into memory | Wait; later calls are faster |

## Keeping Secrets Safe

- Never put an API key in a `.py` file.
- `.env` is listed in `.gitignore`. Do not remove that line.
- Share `.env.example` (no real values), never `.env`.
- Use only the free tier of any hosted provider.

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
