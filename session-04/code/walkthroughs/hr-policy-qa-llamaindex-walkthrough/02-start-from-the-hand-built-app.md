# Step 2 — Start From the Hand-Built App

> Back to index · Previous: Concepts Overview · Next: Load the Documents

## Goal

Copy the finished hand-built app, give the copy its own name, swap in the LlamaIndex
packages, and check that they import.

## Why this matters

The hand-built walkthrough already covered the project folder, the documents, the key and
`.gitignore`. Repeating those steps would teach nothing new, so this walkthrough starts
from a copy of that app and changes only what LlamaIndex changes.

It is a copy and not an edit in place, on purpose. The original stays untouched, so in
Steps 6 to 8 you can run both apps side by side and see exactly what the framework changed.
That comparison is worth more than any description of it.

LlamaIndex is also split into small packages, one for the core and one for each outside
service it connects to. You install only the connections you use, and switching the vector
store later means switching one package. That is why there are four LlamaIndex lines in
the dependency list and not one.

## 1. Copy the App

Run this from the folder that holds your finished `hr-policy-qa`:

```bash
cp -R hr-policy-qa hr-policy-qa-llamaindex
cd hr-policy-qa-llamaindex
rm -rf .venv .chroma uv.lock vectors.json
```

| Removed | Why |
|---|---|
| `.venv` | It points at the original folder and must be rebuilt for the new one |
| `.chroma` | It is the original app's vector store. The new app builds its own |
| `uv.lock` | It pins the old dependency list. `uv sync` writes a new one |
| `vectors.json` | Left over from an earlier version of the app. It may not exist in yours |

Everything else comes along: `docs/`, `.gitignore`, `.env.example`, your `.env` with the
key in it, and the old `ingest.py` and `ask.py`, which you rewrite in the next steps.

## 2. Change `pyproject.toml`

Replace the contents with:

```toml
[project]
name = "hr-policy-qa-llamaindex"
version = "0.1.0"
description = "The HR policy RAG assistant, rebuilt with LlamaIndex"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.0.0",
    "llama-index-core>=0.12.0",
    "llama-index-embeddings-openai>=0.3.0",
    "llama-index-llms-openai>=0.3.0",
    "llama-index-vector-stores-chroma>=0.4.0",
    "python-dotenv>=1.0.0",
]
```

| Package | Used for | Used in |
|---|---|---|
| `llama-index-core` | Readers, node parsers, the index, the retriever, the chat engine | Every step from 3 on |
| `llama-index-embeddings-openai` | The OpenAI embedding model, as a LlamaIndex object | Steps 5 and 6 |
| `llama-index-llms-openai` | The OpenAI chat model, as a LlamaIndex object | Step 7 |
| `llama-index-vector-stores-chroma` | The adapter that lets an index use a Chroma collection | Steps 5 and 6 |
| `chromadb` | Chroma itself, unchanged | Steps 5 and 6 |
| `python-dotenv` | Reading the key from `.env`, unchanged | Steps 5 and 6 |

The `openai` package is no longer listed. It is not gone: the two LlamaIndex OpenAI
packages depend on it, so it is installed anyway, and your code no longer calls it directly.

## 3. Build the Environment

```bash
uv sync
```

This is a larger download than the hand-built app needed, because LlamaIndex brings many
packages with it.

## Try it

Check that the new packages import:

```bash
uv run python -c "import llama_index.core; print('llama-index ok')"
```

```text
llama-index ok
```

Then check that the copied key is still found, without printing it:

```bash
uv run python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('key found' if os.getenv('OPENAI_API_KEY') else 'key missing')"
```

```text
key found
```

## Checkpoint

<details>
<summary>Full <code>pyproject.toml</code></summary>

```toml
[project]
name = "hr-policy-qa-llamaindex"
version = "0.1.0"
description = "The HR policy RAG assistant, rebuilt with LlamaIndex"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.0.0",
    "llama-index-core>=0.12.0",
    "llama-index-embeddings-openai>=0.3.0",
    "llama-index-llms-openai>=0.3.0",
    "llama-index-vector-stores-chroma>=0.4.0",
    "python-dotenv>=1.0.0",
]
```

</details>

This matches the reference project's `pyproject.toml` exactly. The `.gitignore`,
`.env.example` and `docs/` folder need no change: `.chroma/` is still where the store
lives, and the key is still the only secret. Your `uv.lock` is created by `uv sync`, and
its contents may differ slightly. Your `.env` holds your own key and is not compared with
anything.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `cp: hr-policy-qa: No such file or directory` | You ran the command from the wrong folder | `cd` to the folder that contains `hr-policy-qa`, then run it again |
| `ModuleNotFoundError: No module named 'llama_index'` | The command ran without `uv run`, or `uv sync` was skipped or ran in the old folder | Run `uv sync` inside `hr-policy-qa-llamaindex`, and start Python with `uv run` |
| `key missing` | `.env` was not copied, for example because the original lives elsewhere | Run `cp .env.example .env` and paste your key, as in the hand-built walkthrough |
| `uv sync` keeps using the old packages | The old `uv.lock` or `.venv` is still there | Run the `rm -rf` line again, then `uv sync` |

Next: **Step 3 — Load the Documents**.
