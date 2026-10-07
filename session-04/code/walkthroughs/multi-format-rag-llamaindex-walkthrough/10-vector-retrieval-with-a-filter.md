# Step 10 — Vector Retrieval With a Filter

> Back to index · Previous: Embed and Store · Next: Keyword Retrieval With BM25

## Goal

Add to `retrieval.py` a function that opens the stored index and builds a vector retriever,
optionally limited to one file type, plus a helper that labels each result by file and place.

## Why this matters

A retriever takes a question and returns the closest nodes, each with a score. You met it in
the earlier app. Two additions make it right for many formats.

The first is the **filter**. Suppose a user knows the answer is in the PDF. Without a filter,
the spreadsheet rows and FAQ answers compete with the PDF's chunks. A metadata filter says
"only nodes whose `file_type` equals `pdf`" **before** the ranking, so the search never looks
at the others. It works because Step 8 stored `file_type` as exact lower-case text.

The second is the **source label**. An answer is only as trustworthy as the reader's ability
to check it, and "expense_limits.xlsx" is not enough for a 10-row sheet in a 2-sheet
workbook. `describe` turns a node into "file > place", and the place depends on the format:
a page for a PDF, a sheet and row for a spreadsheet, a row for a CSV, and the heading for
Markdown and Word.

## 1. Extend `retrieval.py`

Replace the file with this version. The new parts are the imports, `open_index`,
`build_retrievers` and `describe`:

```python
"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

EMBED_MODEL = "text-embedding-3-small"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)


def open_index():
    collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(COLLECTION)
    return VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))


def build_retrievers(index, file_type=None, top_k=4):
    """Returns the vector retriever, optionally limited to one file type."""
    filters = None
    if file_type:
        filters = MetadataFilters.from_dicts([{"key": "file_type", "value": file_type}])

    # Finds nodes whose meaning is close to the question.
    return index.as_retriever(similarity_top_k=top_k, filters=filters)


def describe(node):
    """A short 'file > where' label for a source node."""
    meta = node.metadata
    kind = meta["file_type"]
    if kind == "pdf":
        where = f"page {meta['page']}"
    elif kind == "xlsx":
        where = f"sheet {meta['sheet']}, row {meta['row']}"
    elif kind == "csv":
        where = f"row {meta['row']}"
    else:
        where = node.text.splitlines()[0].lstrip("# ")
    return f"{meta['file_name']} > {where}"
```

| Part | What it does |
|---|---|
| `open_index()` | Opens the Chroma collection that `ingest.py` filled, and wraps it as a LlamaIndex index. No embedding happens here |
| `MetadataFilters.from_dicts([...])` | Builds the filter from a plain dictionary: the key `file_type` must equal the chosen value |
| `index.as_retriever(similarity_top_k=top_k, filters=filters)` | The vector retriever. With `filters=None` it searches everything |
| `build_retrievers(...)` returns one retriever for now | The name says "retrievers" because it will return three by Step 12 |
| `describe(node)` | Turns a node into `file > place` |

## Try it

```bash
uv run python -c "
from retrieval import build_retrievers, configure_models, describe, open_index
configure_models()
index = open_index()
for label, file_type in [('all files', None), ('pdf only', 'pdf'), ('xlsx only', 'xlsx')]:
    print(label)
    for r in build_retrievers(index, file_type=file_type).retrieve('how long do I have to submit a travel claim?'):
        print(f'  {r.score:.2f}  {describe(r.node)}')
"
```

The sources, not the scores, are the lesson. With the filter set to `pdf`, every line should
name `travel_policy.pdf`, with a page number. With `xlsx`, every line should name
`expense_limits.xlsx`, with a sheet and row. With no filter, the lines can mix files, and the
chunk about submitting a claim within 10 working days (page 3) should be among them. Your
scores will depend on the embedding model and are not shown here.

## Checkpoint

<details>
<summary>Full <code>retrieval.py</code> after this step</summary>

```python
"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

EMBED_MODEL = "text-embedding-3-small"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)


def open_index():
    collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(COLLECTION)
    return VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))


def build_retrievers(index, file_type=None, top_k=4):
    """Returns the vector retriever, optionally limited to one file type."""
    filters = None
    if file_type:
        filters = MetadataFilters.from_dicts([{"key": "file_type", "value": file_type}])

    # Finds nodes whose meaning is close to the question.
    return index.as_retriever(similarity_top_k=top_k, filters=filters)


def describe(node):
    """A short 'file > where' label for a source node."""
    meta = node.metadata
    kind = meta["file_type"]
    if kind == "pdf":
        where = f"page {meta['page']}"
    elif kind == "xlsx":
        where = f"sheet {meta['sheet']}, row {meta['row']}"
    elif kind == "csv":
        where = f"row {meta['row']}"
    else:
        where = node.text.splitlines()[0].lstrip("# ")
    return f"{meta['file_name']} > {where}"
```

</details>

This file is not finished. Steps 11 and 12 extend it.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| With the filter on, results from other file types still appear | The value does not match the stored one exactly, for example `'PDF'` in capitals | Use the lower-case extension without a dot: `pdf`, `xlsx`, `md`, `docx`, `csv` |
| With the filter on, nothing comes back | A value with no matching nodes, for example `'txt'` | Use one of the five types. An empty list is the correct answer for an unknown type |
| `KeyError: 'page'` inside `describe` | A PDF node was ingested without the `page` metadata, or `ingest.py` ran before Step 6 was finished | Check `pdf_nodes` and re-run `ingest.py` |
| `chromadb.errors.InvalidCollectionException` | `ingest.py` has not been run | Run `uv run ingest.py` first |

Next: **Step 11 — Keyword Retrieval With BM25**.
