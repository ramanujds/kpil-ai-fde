# Step 2 — Environment Setup

> Back to index · Previous: Concepts Overview · Next: Configuration

## Goal

Create the project folder, declare its dependencies, let `uv` build the environment, and add
a `.gitignore` so a secret can never be committed by accident.

## Why this matters

This project talks to a network service, so it needs an HTTP library (`httpx`), the OpenAI
SDK (`openai`) and a way to read `.env` files (`python-dotenv`). Declaring them in
`pyproject.toml` and letting `uv sync` install them gives every trainee the same versions
through `uv.lock`, which matters when a tutorial's behaviour depends on library details.

The `.gitignore` is set up **now**, before any secret exists. The most common way an API key
leaks is a `.env` file committed on the very first `git add .`. Ignoring `.env` from the
first minute makes that mistake impossible instead of merely unlikely.

If `uv` is new to you, complete the with-uv Site Status API walkthrough first. This step
uses the same ideas: a `pyproject.toml`, `uv sync` and `uv run`.

## 1. Create the project folder

```bash
mkdir ai-and-python
cd ai-and-python
```

## 2. Create `pyproject.toml`

```toml
[project]
name = "ai-and-python"
version = "0.1.0"
description = "Calling an LLM from Python: raw HTTP and the OpenAI SDK, with Ollama or OpenAI"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.28.1",
    "openai>=3.19.1",
    "python-dotenv>=1.2.3",
]
```

The three entries under `dependencies` are the whole toolbox. `requires-python` says the
project needs Python 3.10 or newer.

## 3. Pin the Python version

Create a file named `.python-version` containing a single line:

```text
3.12
```

This tells `uv` which Python to use. If you skip it, `uv` picks any installed Python that
satisfies `requires-python`.

## 4. Create `.gitignore`

```text
.venv/
__pycache__/
.env
```

| Line | What it keeps out of Git |
|---|---|
| `.venv/` | The environment `uv` builds. It is large and rebuilt from `uv.lock` |
| `__pycache__/` | Compiled Python files |
| `.env` | Your real settings and secrets |

## 5. Sync

```bash
uv sync
```

`uv` creates `.venv`, installs the three packages and writes `uv.lock`.

## Try it

```bash
uv run python -c "import openai, httpx, dotenv; print('imports ok')"
```

Expected output:

```text
imports ok
```

Also confirm Ollama can be reached. It listens on port 11434 and lists the models it has:

```bash
curl http://localhost:11434/api/tags
```

Expect a line of JSON that mentions `llama3:8b`.

## Checkpoint

<details>
<summary>Full <code>pyproject.toml</code></summary>

```toml
[project]
name = "ai-and-python"
version = "0.1.0"
description = "Calling an LLM from Python: raw HTTP and the OpenAI SDK, with Ollama or OpenAI"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.28.1",
    "openai>=3.19.1",
    "python-dotenv>=1.2.3",
]
```

</details>

<details>
<summary>Full <code>.gitignore</code></summary>

```text
.venv/
__pycache__/
.env
```

</details>

This matches the reference project's `pyproject.toml`, `.gitignore` and `.python-version`
exactly. (`uv.lock` is generated for you and is not typed by hand.)

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `uv: command not found` | `uv` is not installed, or the terminal was not reopened after installing | See the install step in the environment setup note |
| `uv sync` reports a TOML error | A missing quote or comma in `pyproject.toml` | Match the checkpoint above exactly |
| `curl` cannot connect to port 11434 | Ollama is not running | Start the Ollama app, then retry |
| `uv run` says there is no project | You are in the wrong folder | `cd` into `ai-and-python`, where `pyproject.toml` lives |

Next: **Step 3 — Configuration**.
