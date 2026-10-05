# Step 5 — Embed and Store with an Index

> Back to index · Previous: Chunk into Nodes · Next: Open the Index and Retrieve

## Goal

Finish `ingest.py`: choose the embedding model once, then let one index call embed every
node and store it in Chroma.

## Why this matters

The hand-built app spent two steps here. It called the embeddings API with the list of
chunk texts, picked the vectors out of the response, and then called `upsert` with ids,
vectors, texts and metadata, all kept in step by hand.

LlamaIndex folds those into one object, the **index**. An index is a vector store plus the
embedding model that fills it. When you give `VectorStoreIndex` your nodes, it embeds them
and writes them to the store in one go. You never touch a vector.

Two ideas to hold on to.

**The embedding model becomes a setting.** `Settings.embed_model` is a single place that
says which model to use, for everything in the program. `ask.py` sets the same value, and
it must be the same one, for the reason you met in the hand-built walkthrough: a question
and a chunk can be compared only if the same model made both vectors.

**The ids are no longer yours.** The hand-built app chose each id, `Leave Policy > Sick
Leave`, so a second run replaced the old chunk. LlamaIndex gives every node a random id.
Run the ingest twice without cleaning up and you would store every node twice, and ask
would return near-identical duplicates. So this version starts from an empty collection
every time. That costs you re-embedding 46 short nodes on each run, a fraction of a cent.
It also fixes a gotcha from the hand-built app: sections deleted from a document no longer
linger in the store.

## 1. Replace the Imports and Choose the Embedding Model

The rest of the file needs more imports. Replace the whole import block at the top with
this one. It also drops the `MetadataMode` import from Step 4, which you no longer need:

```python
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
```

Then, directly below the imports and above the loading code, add the setting.
`load_dotenv()` comes back here, because LlamaIndex's OpenAI classes find the key the same
way the `openai` package did:

```python
# Reads OPENAI_API_KEY from the .env file.
load_dotenv()

# One setting chooses the embedding model for the whole app. ask.py must use the same one.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
```

## 2. Open a Fresh Chroma Collection

After the node parser code, add:

```python
# Steps 3 and 4: the index embeds every node and stores it in Chroma.
# We start from an empty collection so that running this twice does not store duplicates.
client = chromadb.PersistentClient(path=".chroma")
try:
    client.delete_collection("policies_llamaindex")
except Exception:
    pass  # first run: there is nothing to delete yet
collection = client.create_collection("policies_llamaindex", metadata={"hnsw:space": "cosine"})
```

| Part | What it does |
|---|---|
| `PersistentClient(path=".chroma")` | The same store folder as the hand-built app |
| `delete_collection(...)` in a `try` | Removes the old collection if there is one. On the very first run there is none, and Chroma raises an error, which the `except` ignores |
| `create_collection(...)` | Makes an empty collection. A different name from the hand-built `policies`, so the two apps never touch each other's data |
| `{"hnsw:space": "cosine"}` | Compares vectors by angle, as in the hand-built app. Scores in Step 6 rely on this |

## 3. Wrap It and Build the Index

```python
storage_context = StorageContext.from_defaults(
    vector_store=ChromaVectorStore(chroma_collection=collection)
)
VectorStoreIndex(nodes, storage_context=storage_context)

print(f"Stored {collection.count()} nodes. Now run ask.py.")
```

| Part | What it does |
|---|---|
| `ChromaVectorStore(chroma_collection=collection)` | The adapter that lets LlamaIndex read and write that Chroma collection |
| `StorageContext.from_defaults(vector_store=...)` | Tells the index where to put what it builds |
| `VectorStoreIndex(nodes, storage_context=...)` | Embeds every node with `Settings.embed_model` and stores it. This one call replaces the embeddings request and the `upsert` of the hand-built app |
| `collection.count()` | Asks Chroma directly how many nodes arrived, as a check |

Nothing keeps the index object, because ask.py builds its own from the same collection.
The work was done inside the call.

Finally, delete the `print(nodes[8]...)` line from Step 4.

## Try it

```bash
uv run ingest.py
```

```text
Made 46 nodes from 6 documents.
Stored 46 nodes. Now run ask.py.
```

The run needs your key and the network, because the embedding call goes to OpenAI. Run it
a second time. The count must stay at 46. If it doubled, the collection was not cleared.

To look inside Chroma yourself:

```bash
uv run python -c "import chromadb; c = chromadb.PersistentClient(path='.chroma').get_collection('policies_llamaindex'); r = c.peek(1); print(c.count()); print(r['ids'][0]); print(sorted(r['metadatas'][0]))"
```

Expect `46`, then a random id that looks like `98f799b7-e336-4510-9466-5f034dffd26f`, then a list of
metadata keys that includes `file_name` and `header_path` along with several keys LlamaIndex
adds for its own bookkeeping. The id is random, which is the point made above.

## Checkpoint

<details>
<summary>Full <code>ingest.py</code></summary>

```python
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# Reads OPENAI_API_KEY from the .env file.
load_dotenv()

# One setting chooses the embedding model for the whole app. ask.py must use the same one.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Step 1: load every file in docs/. With the llama-index-readers-file package added, it also reads PDF and Word.
# We keep only the file name as metadata. The default also holds the full file path, which would get embedded.
documents = SimpleDirectoryReader(
    "docs", file_metadata=lambda path: {"file_name": Path(path).name}
).load_data()

# Step 2: cut each document into nodes (LlamaIndex's word for chunks), one per heading.
nodes = MarkdownNodeParser().get_nodes_from_documents(documents)
print(f"Made {len(nodes)} nodes from {len(documents)} documents.")

# Steps 3 and 4: the index embeds every node and stores it in Chroma.
# We start from an empty collection so that running this twice does not store duplicates.
client = chromadb.PersistentClient(path=".chroma")
try:
    client.delete_collection("policies_llamaindex")
except Exception:
    pass  # first run: there is nothing to delete yet
collection = client.create_collection("policies_llamaindex", metadata={"hnsw:space": "cosine"})

storage_context = StorageContext.from_defaults(
    vector_store=ChromaVectorStore(chroma_collection=collection)
)
VectorStoreIndex(nodes, storage_context=storage_context)

print(f"Stored {collection.count()} nodes. Now run ask.py.")
```

</details>

This matches the reference project's `ingest.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `AuthenticationError`, or a message about a missing API key | `.env` has no key, or `load_dotenv()` is missing or placed after the model is created | Check `.env` and that `load_dotenv()` runs first |
| `RateLimitError` | Free-tier quota or too many requests | Wait a minute and retry. One run makes one batch of calls |
| The stored count doubles on the second run | The `delete_collection` lines were left out | Restore the `try`/`except` block before `create_collection` |
| `ValueError` or `NotFoundError` raised on the first run, not hidden | The `except Exception:` line is missing | Restore it. The error on a first run is expected and is being ignored on purpose |
| `Collection expecting embedding with dimension ... got ...` later, in `ask.py` | `ask.py` uses a different embedding model from this file | Use the same model name in both files, then delete `.chroma` and re-ingest |

Next: **Step 6 — Open the Index and Retrieve**.
