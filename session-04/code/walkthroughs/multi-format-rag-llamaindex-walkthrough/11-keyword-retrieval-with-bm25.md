# Step 11 — Keyword Retrieval With BM25

> Back to index · Previous: Vector Retrieval With a Filter · Next: Hybrid Retrieval and Comparison

## Goal

Add a second way of searching, by exact words, and save a copy of the node text at ingest
time so that it has something to search.

## Why this matters

Search by meaning is good at "can I get my money back?" and weak at "hotel limit for L3".
To an embedding model, the rows for L2, L3 and L4 mean almost the same thing: a hotel limit
for a grade. The one token that tells them apart, `L3`, is a tiny part of the meaning.

A **keyword search** does the opposite. It counts exact words. The standard method is
**BM25**, and it works in three plain ideas: a node that contains more of the question's words
scores higher, a word found in only a few nodes counts for more than a word found
everywhere (so `L3` beats `the`), and repeating a word endlessly does not keep adding up.

BM25 needs one thing the vector search does not: **the text of all the nodes**, because it
must count how common each word is across the whole collection. Chroma holds the text, but
the simplest dependable arrangement is to save a copy at ingest time, in a LlamaIndex
**docstore**, a plain JSON file. Ingest writes it. Retrieval reads it.

## 1. Add the Docstore Path to `retrieval.py`

Replace `retrieval.py` with this version. New: two imports, `DOCSTORE_PATH`, `open_nodes`, and
the keyword retriever inside `build_retrievers`, which now takes `nodes` and returns two
retrievers:

```python
"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore

EMBED_MODEL = "text-embedding-3-small"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"
DOCSTORE_PATH = ".store/docstore.json"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)


def open_index():
    collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(COLLECTION)
    return VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))


def open_nodes():
    # The keyword retriever needs the node text. ingest.py saved a copy next to the Chroma data.
    return list(SimpleDocumentStore.from_persist_path(DOCSTORE_PATH).docs.values())


def build_retrievers(index, nodes, file_type=None, top_k=4):
    """Returns the vector and keyword retrievers, optionally limited to one file type."""
    filters = None
    if file_type:
        filters = MetadataFilters.from_dicts([{"key": "file_type", "value": file_type}])

    # Finds nodes whose meaning is close to the question.
    vector = index.as_retriever(similarity_top_k=top_k, filters=filters)
    # Finds nodes that share the exact words of the question, such as "L3" or "25,000".
    # BM25Retriever's own filters option did not restrict results when we tried it, so we
    # hand it only the nodes of the chosen file type.
    keyword_nodes = [n for n in nodes if not file_type or n.metadata["file_type"] == file_type]
    keyword = BM25Retriever.from_defaults(nodes=keyword_nodes, similarity_top_k=top_k)
    return vector, keyword


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
| `DOCSTORE_PATH` | Where the saved node text lives. Both `ingest.py` and `retrieval.py` use it |
| `open_nodes()` | Reads the saved copy back as a list of nodes |
| `keyword_nodes = [n for n in nodes if ...]` | The nodes the keyword search is allowed to look at: all of them, or only those of the chosen file type |
| `BM25Retriever.from_defaults(nodes=..., similarity_top_k=top_k)` | Builds the keyword index in memory from those nodes |
| `return vector, keyword` | Two retrievers now. Callers must unpack both |

The comment in the code records a real surprise. `BM25Retriever` has its own `filters`
option, but in our tests it did not restrict the results: a search "limited to csv" still
returned PDF and Excel rows. So the file type filter is applied by choosing which nodes go
in, before the index is built. For the vector retriever the filter works as expected.

## 2. Save the Nodes in `ingest.py`

Add two imports. `SimpleDocumentStore` goes with the other `llama_index` imports, and
`DOCSTORE_PATH` joins the `retrieval` import:

```python
from llama_index.core.storage.docstore import SimpleDocumentStore
```

```python
from retrieval import CHROMA_PATH, COLLECTION, DOCSTORE_PATH, configure_models
```

Then add this block between the node counts and the Chroma code:

```python
# The keyword retriever in ask.py needs the node text, so we save a copy of the nodes.
docstore = SimpleDocumentStore()
docstore.add_documents(nodes)
docstore.persist(DOCSTORE_PATH)
```

## Try it

Run ingest again, so that the docstore is written:

```bash
uv run ingest.py
ls .store
```

```text
Nodes per file type:
  csv   12
  docx  6
  md    7
  pdf   6
  xlsx  10
Stored 41 nodes. Now run ask.py.
docstore.json
```

Now run only the keyword search on three questions:

```bash
uv run python -c "
from retrieval import build_retrievers, configure_models, describe, open_index, open_nodes
configure_models()
_, keyword = build_retrievers(open_index(), open_nodes())
for q in ['hotel limit for L3', 'How many days of sick leave does an L4 get?', 'Can I get reimbursed for a course I paid for myself?']:
    print(q)
    for r in keyword.retrieve(q):
        print(f'  {r.score:6.3f}  {describe(r.node)}')
"
```

```text
hotel limit for L3
   2.552  expense_limits.xlsx > sheet Travel Limits, row 4
   1.539  expense_limits.xlsx > sheet Travel Limits, row 2
   1.539  expense_limits.xlsx > sheet Travel Limits, row 3
   1.539  expense_limits.xlsx > sheet Travel Limits, row 6
How many days of sick leave does an L4 get?
   3.434  expense_limits.xlsx > sheet Leave Entitlement, row 5
   2.565  expense_limits.xlsx > sheet Leave Entitlement, row 4
   2.565  expense_limits.xlsx > sheet Leave Entitlement, row 3
   2.565  expense_limits.xlsx > sheet Leave Entitlement, row 2
Can I get reimbursed for a course I paid for myself?
   5.222  hr_faq.csv > row 13
   1.794  travel_policy.pdf > page 3
   1.228  travel_policy.pdf > page 2
   1.157  hr_faq.csv > row 8
```

This output is the same on every run, because keyword scoring has no randomness. It needs no
embedding calls, only the saved nodes. Read it closely:

| Question | What happened |
|---|---|
| Hotel limit for L3 | Row 4 is the L3 row and scores 2.552. The other rows score 1.539 for sharing "hotel" and "limit". The single token `L3` made the difference |
| Sick leave for an L4 | Row 5 of the Leave Entitlement sheet is L4, and scores highest at 3.434. `L4` plus "sick" and "leave" |
| Course paid for myself | The FAQ row about training courses scores 5.222, far above the rest, because the question reuses its words: "course", "paid for myself" |

This is the strength of keyword search: exact tokens decide. The row numbers are Excel's, so
row 4 is the L3 row (Step 7).

## A Warning: Zero Scores

Keyword search always returns `top_k` results, even when nothing matches. Ask the keyword
search to look only at the FAQ file for a question about hotels:

```bash
uv run python -c "
from retrieval import build_retrievers, configure_models, describe, open_index, open_nodes
configure_models()
_, keyword = build_retrievers(open_index(), open_nodes(), file_type='csv')
for r in keyword.retrieve('hotel limit for L3'):
    print(f'  {r.score:6.3f}  {describe(r.node)}')
"
```

```text
   0.000  hr_faq.csv > row 13
   0.000  hr_faq.csv > row 6
   0.000  hr_faq.csv > row 3
   0.000  hr_faq.csv > row 5
```

Four results, all scored 0.000, in no meaningful order. A score of zero means "no word in
common", not "a weak match". Step 12 merges this list with the vector list, and these rows
will earn rank points there anyway. Exercise 4 asks you to deal with it.

## Checkpoint

<details>
<summary>Full <code>retrieval.py</code> after this step</summary>

```python
"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore

EMBED_MODEL = "text-embedding-3-small"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"
DOCSTORE_PATH = ".store/docstore.json"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)


def open_index():
    collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(COLLECTION)
    return VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))


def open_nodes():
    # The keyword retriever needs the node text. ingest.py saved a copy next to the Chroma data.
    return list(SimpleDocumentStore.from_persist_path(DOCSTORE_PATH).docs.values())


def build_retrievers(index, nodes, file_type=None, top_k=4):
    """Returns the vector and keyword retrievers, optionally limited to one file type."""
    filters = None
    if file_type:
        filters = MetadataFilters.from_dicts([{"key": "file_type", "value": file_type}])

    # Finds nodes whose meaning is close to the question.
    vector = index.as_retriever(similarity_top_k=top_k, filters=filters)
    # Finds nodes that share the exact words of the question, such as "L3" or "25,000".
    # BM25Retriever's own filters option did not restrict results when we tried it, so we
    # hand it only the nodes of the chosen file type.
    keyword_nodes = [n for n in nodes if not file_type or n.metadata["file_type"] == file_type]
    keyword = BM25Retriever.from_defaults(nodes=keyword_nodes, similarity_top_k=top_k)
    return vector, keyword


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

<details>
<summary>Full <code>ingest.py</code> after this step</summary>

```python
from collections import Counter

import chromadb
from dotenv import load_dotenv
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.chroma import ChromaVectorStore

from loaders import load_nodes
from retrieval import CHROMA_PATH, COLLECTION, DOCSTORE_PATH, configure_models

# Reads OPENAI_API_KEY from the .env file.
load_dotenv()
configure_models()

# Steps 1 and 2: read every file in docs/ and cut it into nodes. How it is cut depends on the
# file type. See loaders.py.
nodes = load_nodes("docs")

print("Nodes per file type:")
for file_type, count in sorted(Counter(node.metadata["file_type"] for node in nodes).items()):
    print(f"  {file_type:5} {count}")

# The keyword retriever in ask.py needs the node text, so we save a copy of the nodes.
docstore = SimpleDocumentStore()
docstore.add_documents(nodes)
docstore.persist(DOCSTORE_PATH)

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

This matches the reference project's `ingest.py` exactly. `retrieval.py` is not finished.
Step 12 adds the last part.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: .store/docstore.json` | `ingest.py` was not run again after adding the docstore block | Run `uv run ingest.py` |
| `ValueError: too many values to unpack` or `not enough values` | `build_retrievers` now returns two retrievers, and the caller still unpacks one | Unpack both: `_, keyword = build_retrievers(index, nodes)` |
| `TypeError: build_retrievers() missing 1 required positional argument: 'nodes'` | The caller still uses the Step 10 signature | Pass the nodes: `build_retrievers(index, open_nodes())` |
| A word such as "L3" is found but "A" or "5" never is | The default tokenizer ignores single-character tokens | Expected. Words and codes of two characters or more are searchable |
| A "csv only" keyword search returns PDF rows | The retriever's `filters` option was used instead of filtering the nodes | Filter the node list first, as the code shows |

Next: **Step 12 — Hybrid Retrieval and Comparison**.
