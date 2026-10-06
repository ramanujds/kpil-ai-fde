# Step 2 — Project Setup

> Back to index · Previous: Concepts Overview · Next: Your First Call

## Goal

Create the project folder, declare its dependencies, store your API key safely and let `uv`
build the environment.

## Why this matters

The program depends on two outside things: Python packages and an API key. A missing key is
the most common first error, and it looks alarming. Setting both up now means a failure
later has one cause only, your code.

The key goes in a `.env` file that Git ignores. Never type it into a `.py` file, because a
key in code ends up in Git history.

## 1. Create the Folder and `pyproject.toml`

```bash
mkdir simple-tool-calling
cd simple-tool-calling
```

Create `pyproject.toml`:

```toml
[project]
name = "simple-tool-calling"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "openai>=3.25.0",
    "python-dotenv>=1.2.4",
]
```

`openai` is the library that talks to the model. `python-dotenv` reads your key from the
`.env` file.

## 2. Create `.gitignore`

```text
.venv/
__pycache__/
.env
```

`.venv/` and `__pycache__/` are generated files. `.env` holds your key, so it is ignored
from the start.

## 3. Create `.env.example` and `.env`

`.env.example` is the template that is safe to share:

```text
OPENAI_API_KEY=your-openai-api-key-here
```

Copy it to `.env` and put your real key in the copy:

```bash
cp .env.example .env
```

Open `.env` and replace `your-openai-api-key-here` with the key you were issued. Do not add
quotes or spaces around it.

## 4. Build the Environment

```bash
uv sync
```

## Try it

```bash
uv run python -c "import openai, dotenv; print('ready')"
```

```text
ready
```

## Checkpoint

<details>
<summary>Full <code>pyproject.toml</code></summary>

```toml
[project]
name = "simple-tool-calling"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "openai>=3.25.0",
    "python-dotenv>=1.2.4",
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

<details>
<summary>Full <code>.env.example</code></summary>

```text
OPENAI_API_KEY=your-openai-api-key-here
```

</details>

These match the reference project's files exactly. Your `uv.lock` is created by `uv sync`,
and its contents may differ slightly. Your `.env` is yours alone and is never committed.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `uv: command not found` | uv is not installed | Install uv, then reopen the terminal |
| `uv sync` cannot find a project | You ran it outside the folder with `pyproject.toml` | `cd simple-tool-calling` first |
| `ModuleNotFoundError: openai` later | You ran plain `python` outside the environment | Use `uv run` |
| The key is rejected later | Quotes, spaces or a stray line break in `.env` | Keep the line as `OPENAI_API_KEY=` followed by the key |

Next: **Step 3 — Your First Call**.
