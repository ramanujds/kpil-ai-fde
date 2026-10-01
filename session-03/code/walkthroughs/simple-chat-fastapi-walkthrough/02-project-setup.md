# Step 2 — Project Setup

> Back to index · Previous: Concepts Overview · Next: Your First Endpoint

## Goal

Create the project folder, declare its dependencies, let `uv` build the environment, and
check that Ollama is running with the right model.

## Why this matters

The app depends on two outside things: Python packages and a model server. If either is
missing, the first error you see later is confusing. Checking both now means a failure later
has one cause only, your code.

## 1. Create the Folder and `pyproject.toml`

```bash
mkdir simple-chat-fastapi
cd simple-chat-fastapi
```

Create `pyproject.toml`:

```toml
[project]
name = "simple-chat-fastapi"
version = "0.1.0"
description = "The simple chat app as a FastAPI service with a one-page web UI"
requires-python = ">=3.10"
dependencies = [
    "fastapi[standard]>=0.141.1",
    "openai>=3.19.1",
]
```

`fastapi[standard]` brings FastAPI plus the `fastapi dev` command and the server that runs
it. `openai` is the same SDK used in `simple-chat`; it talks to Ollama as well as OpenAI.
Pydantic, used for the request body in Step 4, comes along with FastAPI.

## 2. Create `.gitignore`

```text
.venv/
__pycache__/
```

Both are generated files that should not be committed. There is no `.env` here because
Ollama needs no key.

## 3. Build the Environment

```bash
uv sync
```

## 4. Check Ollama

```bash
ollama list
```

Look for `llama3:8b` in the list. If it is missing, run `ollama pull llama3:8b` once. If
`ollama list` says it cannot connect, start the Ollama app and try again.

## Try it

```bash
ollama run llama3:8b "Say hello in five words"
```

```text
Hello, it's nice to meet you!
```

The exact words will differ. Any reply means the model server is ready.

## Checkpoint

<details>
<summary>Full <code>pyproject.toml</code></summary>

```toml
[project]
name = "simple-chat-fastapi"
version = "0.1.0"
description = "The simple chat app as a FastAPI service with a one-page web UI"
requires-python = ">=3.10"
dependencies = [
    "fastapi[standard]>=0.141.1",
    "openai>=3.19.1",
]
```

</details>

<details>
<summary>Full <code>.gitignore</code></summary>

```text
.venv/
__pycache__/
```

</details>

These match the reference project's `pyproject.toml` and `.gitignore` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `uv: command not found` | uv is not installed | Install uv, then reopen the terminal |
| `ollama list` cannot connect | The Ollama app is not running | Start it and rerun |
| `llama3:8b` missing from the list | The model was never downloaded | `ollama pull llama3:8b` |
| `uv sync` complains about Python | Python older than 3.10 | Let uv install a newer one or point it at 3.10+ |

Next: **Step 3 — Your First Endpoint**.
