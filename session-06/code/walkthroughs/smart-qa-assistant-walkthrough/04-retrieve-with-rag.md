# Step 4 — Retrieve With RAG

> Back to index · Previous: Ingest the Documents · Next: Your First Agent

## Goal

Write `rag.py`, a function that takes a question and returns the best matching pieces of the
documents, each with a source label and a score, and returns nothing when nothing matches well.

## Why this matters

This is the "R" in RAG, and it decides almost everything about the quality of the answers. If
the search returns the wrong pieces, the best model in the world will write a confident answer
from the wrong page.

Two ideas to hold onto:

**Search by meaning, not by words.** "Can I get a cab home after working late?" shares almost
no words with "Late Shift Taxi", but the embeddings are close. That is why the documents were
embedded in Step 3.

**Knowing when to say nothing.** Every search returns *something*: the closest pieces, however
far away they are. If you pass those to a model, it will do its best with them, and its best may
be invented. So `rag.py` drops any piece scoring below a cut-off. An empty result means "the
documents do not cover this", and the rest of the app can answer honestly.

## 1. Add Two Settings to `config.py`

Add these lines at the end of `config.py`:

```python
# Retrieval settings.
TOP_K = 3  # passages handed to the model
MIN_SCORE = 0.65  # passages scoring below this are dropped (weak match = "not found")
```

`TOP_K` is how many pieces to fetch at most. `MIN_SCORE` is the cut-off. The value 0.65 was
chosen by trying real questions against these documents: relevant pieces scored 0.7 to 0.8, and
unrelated questions scored around 0.6. A different embedding model has a different scale, so
**these numbers belong to `nomic-embed-text`**.

## 2. Write `rag.py`

Create `rag.py`:

<details>
<summary>Full <code>rag.py</code></summary>

```python
"""Retrieval: find the passages in the Chroma collection that best match a question."""

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

import config

_retriever = None


def _get_retriever():
    """Open the Chroma collection that ingest.py filled, the first time it is needed."""
    global _retriever
    if _retriever is None:
        collection = chromadb.PersistentClient(path=config.CHROMA_PATH).get_collection(config.COLLECTION)
        index = VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))
        _retriever = index.as_retriever(similarity_top_k=config.TOP_K)
    return _retriever


def search(question: str) -> list[dict]:
    """Return the matching passages as {source, text, score}, best first.

    Weak matches are dropped. An empty list means "the documents do not cover this".
    """
    passages = []
    for hit in _get_retriever().retrieve(question):
        if hit.score is None or hit.score < config.MIN_SCORE:
            continue
        heading = hit.node.get_content().splitlines()[0].lstrip("# ")
        passages.append(
            {
                "source": f"{hit.node.metadata['file_name']} > {heading}",
                "text": hit.node.get_content(),
                "score": hit.score,
            }
        )
    return passages
```

</details>

| Part | What it does |
|---|---|
| `_retriever = None` and `_get_retriever()` | Opens the Chroma collection the first time it is needed, then reuses it. Opening costs time, and importing `rag.py` should be instant |
| `get_collection(...)` | Opens the collection `ingest.py` filled. It fails with a clear error if you have not run ingest |
| `VectorStoreIndex.from_vector_store(...)` | Wraps the existing collection as an index, without re-embedding anything |
| `as_retriever(similarity_top_k=...)` | An object that, given a question, returns the closest nodes with scores |
| `if hit.score is None or hit.score < config.MIN_SCORE: continue` | The cut-off. Weak matches never leave this file |
| `.splitlines()[0].lstrip("# ")` | The first line of the node is its heading; strip the `#` marks to make a label |
| the returned dicts | `source` (for citing), `text` (for the model to read), `score` (for you to inspect) |

The function returns plain dictionaries, not LlamaIndex objects. Nothing outside this file needs
to know LlamaIndex exists, which is what keeps the two libraries apart.

## Try it

```bash
uv run python -c "
import rag
for q in ['Can I claim a taxi ride home after a late shift?', 'What is the dress code for Mars?']:
    print(q)
    results = rag.search(q)
    for p in results:
        print('  ', round(p['score'], 2), p['source'])
    if not results:
        print('   (nothing)')
"
```

```text
Can I claim a taxi ride home after a late shift?
   0.79 expense_handbook.md > Late Shift Taxi
   0.66 expense_handbook.md > What Can Be Claimed
What is the dress code for Mars?
   (nothing)
```

The taxi question finds the right section first, by a clear margin. The Mars question finds
nothing, and that is the right answer.

Now see what the cut-off is doing. Switch it off for one run:

```bash
uv run python -c "
import rag, config
config.MIN_SCORE = 0.0
for p in rag.search('What is the dress code for Mars?'):
    print(round(p['score'], 2), p['source'])
"
```

```text
0.61 expense_handbook.md > Late Shift Taxi
0.61 expense_handbook.md > What Can Be Claimed
0.6 expense_handbook.md > Expense Handbook
```

Three pieces about expenses for a question about Mars, scoring 0.6. Without the cut-off these
would be handed to a model as "context".

## Checkpoint

The `rag.py` shown in section 2 is the checkpoint, apart from one function, `reset()`, that
Step 13 adds for the browser UI. `config.py` now matches the reference file's first 29 lines.

<details>
<summary>Full <code>config.py</code></summary>

```python
"""Settings shared by every file, read from .env (see .env.example).

Both models run locally in Ollama, so no API key is needed.
"""

import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.1:8b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# One embedding model for the whole app. ingest.py, rag.py and faq.py must all use the
# same one, or the vectors cannot be compared. If you change it, run ingest.py again.
Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
Settings.llm = None  # LlamaIndex only retrieves here. LangChain does all the talking.

# Where the vectors live: a Chroma database on disk, in this folder.
CHROMA_PATH = ".chroma"
COLLECTION = "company_docs"

# Retrieval settings.
TOP_K = 3  # passages handed to the model
MIN_SCORE = 0.65  # passages scoring below this are dropped (weak match = "not found")
```

</details>

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Collection company_docs does not exist` | `ingest.py` has not been run, or was run in another folder | Run `uv run ingest.py` from the project folder |
| Everything returns nothing | `MIN_SCORE` is too high for your embedding model | Print the scores with `MIN_SCORE = 0.0`, then pick a cut-off between "relevant" and "unrelated" |
| Everything returns something, even nonsense | `MIN_SCORE` is too low | Same: raise it above the unrelated scores |
| Scores look very different from the ones here | You changed `EMBED_MODEL` | Run `ingest.py` again, then recalibrate `MIN_SCORE` |

Next: **Step 5 — Your First Agent**.
