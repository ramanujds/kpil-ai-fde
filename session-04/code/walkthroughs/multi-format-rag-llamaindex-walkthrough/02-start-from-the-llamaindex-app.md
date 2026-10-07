# Step 2 — Start From the LlamaIndex App

> Back to index · Previous: Concepts Overview · Next: Make the Sample Data

## Goal

Copy the finished `hr-policy-qa-llamaindex` app, clear out what will be replaced, add the
new packages, and check that they import.

## Why this matters

The earlier walkthroughs already covered the project folder, the key and `.gitignore`.
Repeating them would teach nothing new, so this one starts from a copy and changes only what
this app needs.

It is a copy and not an edit in place, on purpose. The original keeps working, so you can
put the two apps side by side at the end. The collection name will also differ, so they
never share a vector store.

Each new package earns its place. LlamaIndex splits its readers and retrievers into small
packages, so reading a PDF and running a keyword search are separate installs. The Word and
Excel files are read by `python-docx` and `openpyxl`, which are ordinary Python libraries and
not part of LlamaIndex at all. `reportlab` is different again: only the script that writes
the sample PDF uses it, so it goes in a separate `dev` group and is never part of the app.

## 1. Copy the App

Run this from the folder that holds your finished `hr-policy-qa-llamaindex`:

```bash
cp -R hr-policy-qa-llamaindex multi-format-rag-llamaindex
cd multi-format-rag-llamaindex
rm -rf .venv .chroma uv.lock README.md ingest.py ask.py docs/*
```

| Removed | Why |
|---|---|
| `.venv` | It points at the original folder and must be rebuilt for the new one |
| `.chroma` | It is the original app's vector store. The new app builds its own |
| `uv.lock` | It pins the old dependency list. `uv sync` writes a new one |
| `README.md` | It describes the old app |
| `ingest.py`, `ask.py` | Both are rewritten from scratch in later steps. Deleting them now means nothing old runs by accident |
| `docs/*` | The six Markdown policies. This app has its own documents (Step 3) |

What remains: `pyproject.toml`, `.gitignore`, `.env.example`, your `.env` with the key in it,
and an empty `docs/` folder.

## 2. Change `pyproject.toml`

Replace the contents with:

```toml
[project]
name = "multi-format-rag-llamaindex"
version = "0.1.0"
description = "RAG over Markdown, PDF, Excel, Word and CSV files, with chunking chosen per file type and hybrid retrieval"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.0.0",
    "llama-index-core>=0.12.0",
    "llama-index-embeddings-openai>=0.3.0",
    "llama-index-llms-openai>=0.3.0",
    "llama-index-readers-file>=0.4.0",
    "llama-index-retrievers-bm25>=0.5.0",
    "llama-index-vector-stores-chroma>=0.4.0",
    "openpyxl>=3.1.0",
    "python-docx>=1.1.0",
    "python-dotenv>=1.0.0",
]

[dependency-groups]
# Only needed by make_sample_data.py, which writes the PDF, Excel and Word sample files.
dev = [
    "reportlab>=4.0.0",
]
```

| Package | Used for | Used in |
|---|---|---|
| `llama-index-core` | Nodes, parsers, the index, retrievers, the chat engine | Every step |
| `llama-index-readers-file` | `PDFReader`, which gives one document per page | Step 6 |
| `python-docx` | Reading Word files, including their heading styles | Step 5 |
| `openpyxl` | Reading Excel files, sheet by sheet and row by row | Step 7 |
| `llama-index-embeddings-openai`, `llama-index-llms-openai` | The OpenAI embedding and chat models as LlamaIndex objects | Steps 9 and 12 |
| `llama-index-vector-stores-chroma`, `chromadb` | Chroma as the vector store | Steps 9 and 10 |
| `llama-index-retrievers-bm25` | The keyword retriever, built on the `bm25s` package | Step 11 |
| `python-dotenv` | Reading the key from `.env` | Step 9 |
| `reportlab` (dev group) | Writing the sample PDF | Step 3 |

`uv sync` installs the `dev` group by default, so `reportlab` arrives with everything else.

## 3. Ignore the Saved Node Text

The app will keep a copy of the node text in `.store/` (Step 11). Like `.chroma/`, it is
rebuilt by `ingest.py` and should not be committed:

```bash
echo ".store/" >> .gitignore
```

## 4. Build the Environment

```bash
uv sync
```

This is a bigger download than the earlier app needed, because of the extra libraries.

## Try it

Check that the new packages import:

```bash
uv run python -c "import docx, openpyxl, reportlab, bm25s, llama_index.readers.file, llama_index.retrievers.bm25; print('imports ok')"
```

```text
imports ok
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
name = "multi-format-rag-llamaindex"
version = "0.1.0"
description = "RAG over Markdown, PDF, Excel, Word and CSV files, with chunking chosen per file type and hybrid retrieval"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.0.0",
    "llama-index-core>=0.12.0",
    "llama-index-embeddings-openai>=0.3.0",
    "llama-index-llms-openai>=0.3.0",
    "llama-index-readers-file>=0.4.0",
    "llama-index-retrievers-bm25>=0.5.0",
    "llama-index-vector-stores-chroma>=0.4.0",
    "openpyxl>=3.1.0",
    "python-docx>=1.1.0",
    "python-dotenv>=1.0.0",
]

[dependency-groups]
# Only needed by make_sample_data.py, which writes the PDF, Excel and Word sample files.
dev = [
    "reportlab>=4.0.0",
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
.store/
```

</details>

These match the reference project's `pyproject.toml` and `.gitignore` exactly. The
`.env.example` needs no change. Your `uv.lock` is written by `uv sync` and may differ
slightly. Your `.env` holds your own key and is not compared with anything.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `cp: hr-policy-qa-llamaindex: No such file or directory` | You ran the command from the wrong folder | `cd` to the folder that contains `hr-policy-qa-llamaindex`, then run it again |
| `ModuleNotFoundError: No module named 'docx'` | `uv sync` was skipped, or Python was started without `uv run` | Run `uv sync` in the new folder and start Python with `uv run`. Note that the package is `python-docx`, but the import is `docx` |
| `key missing` | `.env` was not copied | Run `cp .env.example .env` and paste your key |
| `ModuleNotFoundError: No module named 'reportlab'` in Step 3 | The `dev` group was not installed, for example `uv sync --no-dev` was used | Run `uv sync` again without that flag |

Next: **Step 3 — Make the Sample Data**.
