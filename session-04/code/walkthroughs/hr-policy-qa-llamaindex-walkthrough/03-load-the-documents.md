# Step 3 — Load the Documents

> Back to index · Previous: Start From the Hand-Built App · Next: Chunk into Nodes

## Goal

Start the new `ingest.py`: load every file in `docs/` with LlamaIndex's reader, keeping
only the metadata worth keeping.

## Why this matters

In the hand-built app, loading meant a loop over `Path("docs").glob("*.md")` and a call to
`read_text()`. That works for Markdown and nothing else. A real folder of policies holds
PDF and Word files too, and a loop written for one format has to be rewritten for each.

A **reader** hides that. `SimpleDirectoryReader` walks a folder, picks a way to read each
file type, and returns **documents**: one object per file, holding the whole text and some
metadata. The reader reads Markdown and plain text on its own. For PDF and Word you add one
more package, `llama-index-readers-file`, and the same two lines keep working.

The metadata needs one decision. By default the reader records the file name, the full file
path, the size and two dates. The embedding step later includes some of that metadata, and
the full file path is **not** among the parts LlamaIndex hides from it. So a path such as
`/Users/you/projects/hr-policy-qa-llamaindex/docs/02_leave_policy.md` would be mixed into
the text that gets embedded, and later shown to the model. That is noise at best, and it
leaks the layout of your machine at worst. The fix is to say exactly which metadata you
want.

## 1. Replace the Old File

Open `ingest.py`. It still holds the hand-built version. Delete everything in it. Each
part of that code has a replacement in the next three steps, and the original is still
safe in `hr-policy-qa`.

## 2. Read the Folder

```python
from pathlib import Path

from llama_index.core import SimpleDirectoryReader

# Step 1: load every file in docs/. With the llama-index-readers-file package added, it also reads PDF and Word.
# We keep only the file name as metadata. The default also holds the full file path, which would get embedded.
documents = SimpleDirectoryReader(
    "docs", file_metadata=lambda path: {"file_name": Path(path).name}
).load_data()
```

| Part | What it does |
|---|---|
| `SimpleDirectoryReader("docs")` | Reads every file in the `docs` folder |
| `file_metadata=...` | A small function the reader calls for every file. Whatever dictionary it returns becomes that document's metadata |
| `lambda path: {...}` | A one-line function. It receives the file's path and returns `{"file_name": "02_leave_policy.md"}` |
| `Path(path).name` | The file name without its folders, as in the hand-built app |
| `.load_data()` | Does the reading and returns a list of documents |

## 3. Look at What You Loaded

At the end of the file, add two lines for looking at the result. You will remove them in
Step 4:

```python
print(f"Loaded {len(documents)} documents.")
print(documents[0].metadata)
print(documents[0].text.splitlines()[0])
```

## Try it

```bash
uv run ingest.py
```

```text
Loaded 6 documents.
{'file_name': '01_hr_handbook.md'}
# HR Handbook
```

There are six documents, one per file, and each one still holds its whole text, headings
and all. Nothing has been cut up yet. That is the next step.

To see why the `file_metadata` line matters, delete it for a moment and run again. The
metadata then lists the file path, size and dates as well. Put it back afterwards.

## Checkpoint

<details>
<summary>Full <code>ingest.py</code> after this step</summary>

```python
from pathlib import Path

from llama_index.core import SimpleDirectoryReader

# Step 1: load every file in docs/. With the llama-index-readers-file package added, it also reads PDF and Word.
# We keep only the file name as metadata. The default also holds the full file path, which would get embedded.
documents = SimpleDirectoryReader(
    "docs", file_metadata=lambda path: {"file_name": Path(path).name}
).load_data()

print(f"Loaded {len(documents)} documents.")
print(documents[0].metadata)
print(documents[0].text.splitlines()[0])
```

</details>

This file is not finished. Steps 4 and 5 add to it, and Step 5 holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Loaded 0 documents` or a `ValueError` saying the directory does not exist | `docs` was not found, usually because you ran the command from a different folder | Run `uv run ingest.py` from the folder that contains `docs` and `ingest.py` |
| `ModuleNotFoundError: No module named 'llama_index'` | Step 2 was skipped, or the command ran without `uv run` | Run `uv sync`, then `uv run ingest.py` |
| The metadata also shows `file_path`, `file_size` and dates | The `file_metadata=...` argument is missing or misspelt | Restore it exactly as shown |
| A PDF fails to load or comes back as unreadable text | PDF support needs the extra reader package | Add `llama-index-readers-file` to the dependencies and run `uv sync` |

Next: **Step 4 — Chunk into Nodes**.
