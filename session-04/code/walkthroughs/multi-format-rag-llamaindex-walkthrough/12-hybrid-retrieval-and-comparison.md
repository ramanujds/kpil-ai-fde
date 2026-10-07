# Step 12 — Hybrid Retrieval and Comparison

> Back to index · Previous: Keyword Retrieval With BM25 · Next: Answer With a Chat Engine

## Goal

Merge the vector and keyword searches into one hybrid retriever, and write a script that
prints all three lists side by side.

## Why this matters

You now have two searches that fail in opposite ways. Merging them gives a third that is
rarely lost: when one list misses the right node, the other still holds it.

The merge has a trap. The vector score is a similarity between 0 and 1. The BM25 score is
unbounded: you just saw 5.222 and 2.552. Adding them would let the keyword score swamp the
other, and the numbers do not mean the same thing anyway. So the merge ignores scores and
uses only each node's **position** in each list. This is **reciprocal rank fusion**. A node
earns `1 / (60 + position)` from each list it appears in, and the totals decide the final
order. A node that **both** searches rank highly wins over a node that only one of them
loves.

The top possible score with two lists is a node ranked first in both: `1/61 + 1/61`, about
0.033. That is why fused scores are small numbers, around 0.01 to 0.03, and cannot be
compared with the similarity scores of the earlier app. This is also why the app has no
similarity cut-off.

## 1. Extend `retrieval.py`

Replace `retrieval.py` with the final version. New: two imports, `CHAT_MODEL`, the chat model
in `configure_models`, the fusion retriever, and a return of three retrievers:

```python
"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"
DOCSTORE_PATH = ".store/docstore.json"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)
    # Only ask.py uses the chat model to answer. The fusion retriever below also wants an LLM
    # object to exist, though with num_queries=1 it never calls it.
    Settings.llm = OpenAI(model=CHAT_MODEL)


def open_index():
    collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(COLLECTION)
    return VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))


def open_nodes():
    # The keyword retriever needs the node text. ingest.py saved a copy next to the Chroma data.
    return list(SimpleDocumentStore.from_persist_path(DOCSTORE_PATH).docs.values())


def build_retrievers(index, nodes, file_type=None, top_k=4):
    """Returns (vector, keyword, hybrid) retrievers, optionally limited to one file type."""
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
    # Merges the two ranked lists. num_queries=1 means the question is not rewritten into
    # several variants, so no extra model call is made.
    hybrid = QueryFusionRetriever(
        [vector, keyword],
        similarity_top_k=top_k,
        num_queries=1,
        mode="reciprocal_rerank",
        use_async=False,
    )
    return vector, keyword, hybrid


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
| `QueryFusionRetriever([vector, keyword], ...)` | Runs both retrievers and merges their lists |
| `mode="reciprocal_rerank"` | Merge by position, not score |
| `similarity_top_k=top_k` | Keep the best 4 after merging |
| `num_queries=1` | Use the question as written. A larger number asks a model to write variations of the question and search with each, which costs an extra model call |
| `use_async=False` | Run the two searches one after the other, which keeps the program simple |
| `Settings.llm = OpenAI(model=CHAT_MODEL)` | The fusion retriever wants a chat model to exist, even though `num_queries=1` never calls it. Setting it ourselves means the choice is ours and not a hidden default |
| `return vector, keyword, hybrid` | All three, so that the comparison script and the chat engine can pick |

## 2. Create `compare_retrieval.py`

Create `compare_retrieval.py`:

```python
import sys

from dotenv import load_dotenv

from retrieval import build_retrievers, configure_models, describe, open_index, open_nodes

load_dotenv()
configure_models()

# Questions that mix exact codes and plain meaning. Pass your own as arguments:
#   uv run compare_retrieval.py "your question here"
QUESTIONS = [
    "hotel limit for L3",
    "How many days of sick leave does an L4 get?",
    "Do I need approval for a trip that costs 30,000 INR?",
    "Can I get reimbursed for a course I paid for myself?",
]

questions = sys.argv[1:] or QUESTIONS
vector, keyword, hybrid = build_retrievers(open_index(), open_nodes(), top_k=3)

for question in questions:
    print(f"\nQuestion: {question}")
    for name, retriever in [("vector", vector), ("keyword", keyword), ("hybrid", hybrid)]:
        print(f"  {name}:")
        for result in retriever.retrieve(question):
            print(f"    {result.score:7.3f}  {describe(result.node)}")
```

| Part | What it does |
|---|---|
| `QUESTIONS` | Four questions: an exact code, a code in a sentence, a number, and a loosely worded one |
| `sys.argv[1:] or QUESTIONS` | Questions typed after the script name replace the built-in ones |
| `top_k=3` | Three results each, to keep the output short |
| The loops | Print each retriever's list with scores and `describe` labels. No model writes an answer here |

## Try it

```bash
uv run compare_retrieval.py "hotel limit for L3"
```

```text
Question: hotel limit for L3
  vector:
      0.xxx  ...
      0.xxx  ...
      0.xxx  ...
  keyword:
      2.552  expense_limits.xlsx > sheet Travel Limits, row 4
      1.539  expense_limits.xlsx > sheet Travel Limits, row 3
      1.539  expense_limits.xlsx > sheet Travel Limits, row 2
  hybrid:
      0.0xx  ...
      0.0xx  ...
      0.0xx  ...
```

The keyword block is what you will see (the order of the two tied 1.539 rows can differ). The
vector and hybrid blocks depend on your embedding model, so their lines are shown as
placeholders. Read them as follows:

| Block | What to look for |
|---|---|
| vector | Scores between 0 and 1. Probably several grades' rows, since "hotel limit" is their shared meaning. Is the L3 row first? |
| keyword | The L3 row first, with a clear gap to the next |
| hybrid | Scores around 0.016 to 0.033. A node in both lists above the others. Is the L3 row at or near the top? |

Now run it with no argument to try the four built-in questions, and for each one compare the
three lists. The loosely worded question about a course should show the opposite pattern to
the L3 question: the vector search does the heavy lifting there.

## Checkpoint

<details>
<summary>Full <code>retrieval.py</code></summary>

```python
"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"
DOCSTORE_PATH = ".store/docstore.json"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)
    # Only ask.py uses the chat model to answer. The fusion retriever below also wants an LLM
    # object to exist, though with num_queries=1 it never calls it.
    Settings.llm = OpenAI(model=CHAT_MODEL)


def open_index():
    collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(COLLECTION)
    return VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))


def open_nodes():
    # The keyword retriever needs the node text. ingest.py saved a copy next to the Chroma data.
    return list(SimpleDocumentStore.from_persist_path(DOCSTORE_PATH).docs.values())


def build_retrievers(index, nodes, file_type=None, top_k=4):
    """Returns (vector, keyword, hybrid) retrievers, optionally limited to one file type."""
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
    # Merges the two ranked lists. num_queries=1 means the question is not rewritten into
    # several variants, so no extra model call is made.
    hybrid = QueryFusionRetriever(
        [vector, keyword],
        similarity_top_k=top_k,
        num_queries=1,
        mode="reciprocal_rerank",
        use_async=False,
    )
    return vector, keyword, hybrid


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
<summary>Full <code>compare_retrieval.py</code></summary>

```python
import sys

from dotenv import load_dotenv

from retrieval import build_retrievers, configure_models, describe, open_index, open_nodes

load_dotenv()
configure_models()

# Questions that mix exact codes and plain meaning. Pass your own as arguments:
#   uv run compare_retrieval.py "your question here"
QUESTIONS = [
    "hotel limit for L3",
    "How many days of sick leave does an L4 get?",
    "Do I need approval for a trip that costs 30,000 INR?",
    "Can I get reimbursed for a course I paid for myself?",
]

questions = sys.argv[1:] or QUESTIONS
vector, keyword, hybrid = build_retrievers(open_index(), open_nodes(), top_k=3)

for question in questions:
    print(f"\nQuestion: {question}")
    for name, retriever in [("vector", vector), ("keyword", keyword), ("hybrid", hybrid)]:
        print(f"  {name}:")
        for result in retriever.retrieve(question):
            print(f"    {result.score:7.3f}  {describe(result.node)}")
```

</details>

This matches the reference project's `retrieval.py` and `compare_retrieval.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ValueError: not enough values to unpack` in a script from Step 10 or 11 | `build_retrievers` now returns three retrievers | Unpack three: `vector, keyword, hybrid = ...` |
| An error about the LLM or an API key when building the fusion retriever | `Settings.llm` is not set, so LlamaIndex tries to create a default one | Keep `Settings.llm = OpenAI(model=CHAT_MODEL)` in `configure_models` |
| Hybrid scores are all 0.016 or similar and look "low" | They are rank points, not similarities | Expected. Compare their order, not their size, and not with the vector scores |
| Hybrid returns fewer than `top_k` results | Both lists were shorter, or overlapped completely | Expected for tiny filtered sets |
| The three lists look identical | The question is easy for both searches | Try a question that uses exact codes, and one that is worded loosely |

Next: **Step 13 — Answer With a Chat Engine**.
