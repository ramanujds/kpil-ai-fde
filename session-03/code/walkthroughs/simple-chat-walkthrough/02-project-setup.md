# Step 2 — Project Setup

> Back to index · Previous: Concepts Overview · Next: Your First Call

## Goal

Create the project folder, declare its dependencies, let `uv` build the environment, and
check that Ollama is running with the right model.

## Why this matters

The app depends on two outside things: Python packages and a model server. If either is
missing, the first error you see is confusing. Checking both now means a failure later has
one cause only, your code.

## 1. Create the Folder and `pyproject.toml`

```bash
mkdir simple-chat
cd simple-chat
```

Create `pyproject.toml`:

```toml
[project]
name = "simple-chat"
version = "0.1.0"
description = "The most basic chat app: one question in, one answer out, no memory"
requires-python = ">=3.10"
dependencies = [
    "ollama>=0.6.3",
    "openai>=3.19.1",
    "python-dotenv>=1.2.3",
]
```

You will use `openai` in Steps 3 to 6, `ollama` in Step 5 and `python-dotenv` in Step 6.
Declaring all three now saves a stop later.

## 2. Create `.gitignore`

```text
.venv/
__pycache__/
.env
```

`.venv/` and `__pycache__/` are generated files. `.env` is where your API key will live in
Step 6, so it is ignored from the start.

## 3. Build the Environment

```bash
uv sync
```

## 4. Check Ollama

```bash
ollama list
```

Look for `llama3:8b` in the list. If it is missing, download it once:

```bash
ollama pull llama3:8b
```

If `ollama list` says it cannot connect, start the Ollama app and try again.

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
name = "simple-chat"
version = "0.1.0"
description = "The most basic chat app: one question in, one answer out, no memory"
requires-python = ">=3.10"
dependencies = [
    "ollama>=0.6.3",
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

These match the reference project's `pyproject.toml` and `.gitignore` exactly. Your
`uv.lock` is created by `uv sync`, and its contents may differ slightly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ollama: command not found` | Ollama is not installed | Install Ollama, then reopen the terminal |
| `could not connect to ollama app` | Ollama is installed but not running | Start the Ollama app |
| `uv: command not found` | uv is not installed | Install uv, then reopen the terminal |
| `uv sync` cannot find a project | You ran it outside the folder with `pyproject.toml` | `cd simple-chat` first |

Next: **Step 3 — Your First Call**.
