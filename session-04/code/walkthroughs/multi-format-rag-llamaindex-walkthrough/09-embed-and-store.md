# Step 9 — Embed and Store

> Back to index · Previous: Route by File Type · Next: Vector Retrieval With a Filter

## Goal

Create `retrieval.py` with the shared model settings, and write `ingest.py`: load the nodes,
embed them and store them in a Chroma collection, with their metadata.

## Why this matters

`loaders.py` produces nodes. Now they must become searchable. That is the same two steps as
in the earlier LlamaIndex app, embedding and storing, done by the same call. What differs is
how the code is organised.

Both scripts need the same embedding model. If `ingest.py` used one model and `ask.py`
another, the stored vectors and the question vectors would come from different spaces and
the distances between them would mean nothing. The earlier app avoided this by repeating the
model name in both files and warning you to keep them equal. Here the choice lives once, in
`retrieval.py`, and both scripts call `configure_models()`. A shared module is also where
the retrievers will go in Steps 10 to 12.

The Chroma metadata matters too. Each stored node keeps `file_name`, `file_type`, `page`,
`sheet` and `row`. That is what lets Step 10 say "only the nodes whose `file_type` is `pdf`".

## 1. Create `retrieval.py`

Create `retrieval.py` with the settings only. The rest is added in Steps 10 to 12:

```python
"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

EMBED_MODEL = "text-embedding-3-small"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)
```

| Line | What it does |
|---|---|
| `EMBED_MODEL`, `CHROMA_PATH`, `COLLECTION` | The three facts that `ingest.py` and `ask.py` must agree on |
| `configure_models()` | Sets the one embedding model that LlamaIndex uses whenever it needs vectors |

The docstring mentions `compare_retrieval.py`, which does not exist until Step 12. It is
describing where the module will be used.

## 2. Create `ingest.py`

Create `ingest.py`:

```python
from collections import Counter

import chromadb
from dotenv import load_dotenv
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from loaders import load_nodes
from retrieval import CHROMA_PATH, COLLECTION, configure_models

# Reads OPENAI_API_KEY from the .env file.
load_dotenv()
configure_models()

# Steps 1 and 2: read every file in docs/ and cut it into nodes. How it is cut depends on the
# file type. See loaders.py.
nodes = load_nodes("docs")

print("Nodes per file type:")
for file_type, count in sorted(Counter(node.metadata["file_type"] for node in nodes).items()):
    print(f"  {file_type:5} {count}")

# Steps 3 and 4: embed every node and store it in Chroma, with its metadata.
# We start from an empty collection so that running this twice does not store duplicates.
client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    client.delete_collection(COLLECTION)
except Exception:
    pass  # first run: there is nothing to delete yet
collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

storage_context = StorageContext.from_defaults(
    vector_store=ChromaVectorStore(chroma_collection=collection)
)
VectorStoreIndex(nodes, storage_context=storage_context)

print(f"Stored {collection.count()} nodes. Now run ask.py.")
```

| Block | What it does |
|---|---|
| `load_dotenv()` and `configure_models()` | Reads the key from `.env`, then sets the embedding model |
| `load_nodes("docs")` | Steps 1 and 2 of RAG, all in `loaders.py`. Ingest does not know there are five formats |
| The `Counter` loop | Prints how many nodes each format produced, so you can see the effect of each strategy |
| `delete_collection` in a `try` | The same trick as the earlier app: nodes get random ids, so ingesting twice would store everything twice. Starting empty avoids it |
| `create_collection(..., metadata={"hnsw:space": "cosine"})` | A new collection that measures closeness by cosine similarity |
| `VectorStoreIndex(nodes, storage_context=...)` | Embeds every node and writes it to Chroma, with its metadata, in one call |

The final line prints "Now run ask.py". That script does not exist yet. For now, treat it as
a pointer for later.

## Try it

This step calls the embedding API, so the key in `.env` must be real:

```bash
uv run ingest.py
```

```text
Nodes per file type:
  csv   12
  docx  6
  md    7
  pdf   6
  xlsx  10
Stored 41 nodes. Now run ask.py.
```

Then look at what Chroma stored for one spreadsheet row, without the large internal fields:

```bash
uv run python -c "
import chromadb
c = chromadb.PersistentClient(path='.chroma').get_collection('multi_format_docs')
print(c.count())
m = c.get(limit=1, where={'file_type': 'xlsx'}, include=['metadatas'])['metadatas'][0]
print({k: v for k, v in m.items() if not k.startswith('_')})
"
```

```text
41
{'row': 2, 'file_name': 'expense_limits.xlsx', 'doc_id': 'None', 'document_id': 'None', 'sheet': 'Travel Limits', 'ref_doc_id': 'None', 'file_type': 'xlsx'}
```

The `where={'file_type': 'xlsx'}` in that command is a metadata filter, written in Chroma's
own language. Step 10 does the same thing through LlamaIndex.

## Checkpoint

<details>
<summary>Full <code>retrieval.py</code> after this step</summary>

```python
"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

EMBED_MODEL = "text-embedding-3-small"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)
```

</details>

<details>
<summary>Full <code>ingest.py</code> after this step</summary>

```python
from collections import Counter

import chromadb
from dotenv import load_dotenv
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from loaders import load_nodes
from retrieval import CHROMA_PATH, COLLECTION, configure_models

# Reads OPENAI_API_KEY from the .env file.
load_dotenv()
configure_models()

# Steps 1 and 2: read every file in docs/ and cut it into nodes. How it is cut depends on the
# file type. See loaders.py.
nodes = load_nodes("docs")

print("Nodes per file type:")
for file_type, count in sorted(Counter(node.metadata["file_type"] for node in nodes).items()):
    print(f"  {file_type:5} {count}")

# Steps 3 and 4: embed every node and store it in Chroma, with its metadata.
# We start from an empty collection so that running this twice does not store duplicates.
client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    client.delete_collection(COLLECTION)
except Exception:
    pass  # first run: there is nothing to delete yet
collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

storage_context = StorageContext.from_defaults(
    vector_store=ChromaVectorStore(chroma_collection=collection)
)
VectorStoreIndex(nodes, storage_context=storage_context)

print(f"Stored {collection.count()} nodes. Now run ask.py.")
```

</details>

Neither file is finished. Steps 10 to 12 extend `retrieval.py`, and Step 11 adds a block to
`ingest.py`.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `AuthenticationError` or `Incorrect API key` | `.env` is missing, or holds the placeholder from `.env.example` | Put your real key in `.env`, with no quotes |
| `ModuleNotFoundError: No module named 'loaders'` or `'retrieval'` | The script runs from another folder | Run `uv run ingest.py` from the project folder |
| `Stored 82 nodes` after two runs | The `delete_collection` lines were left out | Restore them. Node ids are random, so a rerun cannot replace the old nodes |
| `RateLimitError` | The free tier's limit was reached | Wait a minute and run again. 41 short nodes need only a few calls |
| `chromadb.errors.InvalidCollectionException` in Step 10 | Ingest has not been run, or the collection name differs between the two files | Run `ingest.py`, and keep the name in `retrieval.py` only |

Next: **Step 10 — Vector Retrieval With a Filter**.
