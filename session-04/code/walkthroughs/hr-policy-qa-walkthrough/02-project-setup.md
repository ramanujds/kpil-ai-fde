# Step 2 — Project Setup

> Back to index · Previous: Concepts Overview · Next: The Documents

## Goal

Create the project folder, declare its dependencies, put your API key in a `.env` file that
Git ignores, and check that the key is found.

## Why this matters

This app depends on three outside things: Python packages, an API key, and a folder the
vector store can write to. If any of them is wrong, the first error you see is confusing
and looks like a problem in your code. Checking each now means that a later failure has
one cause only.

The key needs the most care. Anything saved in a file that Git tracks can end up in a
public repository. The `.env` file holds the key and `.gitignore` keeps that file out of
Git from the very first commit. `.env.example` is the copy that is safe to share: it shows
which variable is needed without holding a real key.

## 1. Create the Folder and `pyproject.toml`

```bash
mkdir hr-policy-qa
cd hr-policy-qa
```

Create `pyproject.toml`:

```toml
[project]
name = "hr-policy-qa"
version = "0.1.0"
description = "A simple RAG question-answering assistant over synthetic company policy documents"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.0.0",
    "openai>=1.50.0",
    "python-dotenv>=1.0.0",
]
```

| Package | Used for | Used in |
|---|---|---|
| `openai` | Embeddings and the chat model | Steps 5, 7 and 8 |
| `chromadb` | The vector store | Steps 6 and 7 |
| `python-dotenv` | Reading the key from `.env` | Steps 5 and 7 |

## 2. Create `.gitignore`

```text
.venv/
__pycache__/
.env
.chroma/
```

`.venv/` and `__pycache__/` are generated files. `.env` holds your key. `.chroma/` is the
vector store that Step 6 creates; it is rebuilt from the documents at any time, so it does
not belong in Git.

## 3. Create `.env.example` and `.env`

Create `.env.example`:

```text
OPENAI_API_KEY=your-openai-api-key-here
```

Now copy it to `.env`:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your real key. Only `.env` ever holds the
real key.

## 4. Build the Environment

```bash
uv sync
```

The first run downloads Chroma and its dependencies, so it takes noticeably longer than in
the earlier projects.

## Try it

Check that the key is found, without printing it:

```bash
uv run python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('key found' if os.getenv('OPENAI_API_KEY') else 'key missing')"
```

```text
key found
```

Then check that Git ignores the file:

```bash
git check-ignore -v .env
```

If you are inside a Git repository, this prints the `.gitignore` line that matches `.env`.

## Checkpoint

<details>
<summary>Full <code>pyproject.toml</code></summary>

```toml
[project]
name = "hr-policy-qa"
version = "0.1.0"
description = "A simple RAG question-answering assistant over synthetic company policy documents"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.0.0",
    "openai>=1.50.0",
    "python-dotenv>=1.0.0",
]
```

</details>

<details>
<summary>Full <code>.gitignore</code></summary>

```text
.venv/
__pycache__/
.env
.chroma/
```

</details>

<details>
<summary>Full <code>.env.example</code></summary>

```text
OPENAI_API_KEY=your-openai-api-key-here
```

</details>

These match the reference project's `pyproject.toml`, `.gitignore` and `.env.example`
exactly. Your `uv.lock` is created by `uv sync`, and its contents may differ slightly. Your
`.env` holds your own key and is not compared with anything.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `key missing` | The file is named `.env.txt`, or sits in the wrong folder, or the variable name is misspelt | The file must be called exactly `.env`, in the folder with `pyproject.toml`, with the line `OPENAI_API_KEY=...` |
| `uv: command not found` | uv is not installed | Install uv, then reopen the terminal |
| `uv sync` cannot find a project | You ran it outside the folder with `pyproject.toml` | `cd hr-policy-qa` first |
| `git status` lists `.env` | `.gitignore` is missing or has a typo | Fix `.gitignore`. If `.env` was already committed, the key is exposed: revoke it and create a new one |

Next: **Step 3 — The Documents**.
