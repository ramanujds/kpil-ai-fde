# Step 3 — The Search Tool

> Back to index · Previous: Start From the Hand-Built App · Next: Describe the Tool and Let the Model Decide

## Goal

Turn the retrieval you already wrote into a function that the model will later be allowed to
call: it takes a query, optionally limits the search to one document, and returns the
closest chunks with a relevance score.

## Why this matters

In the hand-built `ask.py`, retrieval was three lines in the middle of the loop. The
question went in, four chunks came out, and nothing downstream could change how that went.

A **tool** is the same retrieval, moved into a function with a name. Two small changes make
it fit for an agent:

1. **A choice of where to look.** The `document` argument limits the search to one policy.
   The model can send "notice period" to the HR Handbook only, so the laptop and expense
   policies cannot crowd the results.
2. **A score it can judge.** The hand-built app printed which chunks came back but gave no
   hint of how good they were. Chroma returns a distance, where smaller is closer. The tool
   turns it into a relevance from 0 to 1, where bigger is better. A model that can see
   "0.09" next to a chunk can decide that the search failed and try again. A model that
   sees only text will happily answer from a bad match.

Nothing here involves the model yet. Writing the tool as an ordinary function first means
you can test it on its own, with no model to blame if the results look wrong.

## 1. Set Up the Connections

Create `ask.py`. The first lines are the same as the hand-built app: read the key, create
the client, open the collection that `ingest.py` filled. One new line makes a list for the
sources the tool reads, so they can be shown at the end.

```python
import json

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

collection = chromadb.PersistentClient(path=".chroma").get_collection("policies")

# Sources of every chunk the agent reads while answering one question.
retrieved = []
```

## 2. Write the Tool

Below it, add the function:

```python


# ---------------------------------------------------------------------------
# The tools: ordinary Python functions the model is allowed to ask for.
# ---------------------------------------------------------------------------
def search_policies(query, document=None):
    embedding = client.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding
    result = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        where={"source": document} if document else None,
    )
    found = []
    for text, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        retrieved.append(f"{meta['source']} > {meta['section']}")
        # Cosine distance becomes a 0-to-1 relevance score the model can judge.
        found.append({"source": meta["source"], "section": meta["section"], "relevance": round(1 - distance, 2), "text": text})
    return json.dumps(found)
```

| Part | What it does |
|---|---|
| `embedding = client.embeddings.create(...)` | The same embedding call as the hand-built app, with the same model |
| `n_results=3` | Three chunks, not four. In an agent a search can run several times, so each one is kept smaller |
| `where={"source": document} if document else None` | Filter on the `source` metadata that `ingest.py` stored, which is the document title. With no document, search everything |
| `1 - distance` | The collection was made with cosine distance, so one minus the distance is a similarity. Closer to 1 means a better match |
| `retrieved.append(...)` | Remembers where each chunk came from, for the "Retrieved from" list later |
| `json.dumps(found)` | A tool must return text. JSON is easy for the model to read and keeps the fields apart |

## Try it

You can already run the function without any model, by importing your own file:

```bash
uv run python -c "import ask, json; [print(r['source'], '|', r['section'], '|', r['relevance']) for r in json.loads(ask.search_policies('How long is the notice period?', 'HR Handbook'))]"
```

```text
HR Handbook | Notice Period | 0.65
HR Handbook | Probation | 0.43
HR Handbook | Grievance Redressal | 0.39
```

The right section is first, with a clearly higher score. Now search everything by leaving
the document out:

```bash
uv run python -c "import ask, json; [print(r['source'], '|', r['section'], '|', r['relevance']) for r in json.loads(ask.search_policies('How long is the notice period?'))]"
```

```text
HR Handbook | Notice Period | 0.65
Leave Policy | How to Apply for Leave | 0.5
HR Handbook | Probation | 0.43
```

The filter changed the second result. Finally, search for something no document covers:

```bash
uv run python -c "import ask, json; [print(r['source'], '|', r['section'], '|', r['relevance']) for r in json.loads(ask.search_policies('capital of France'))]"
```

```text
Laptop and Equipment Policy | Accessories | 0.11
Laptop and Equipment Policy | Returning Equipment | 0.09
Expense Reimbursement Policy | Meal Allowance | 0.09
```

Three chunks still come back, as they always do, but the scores are around 0.1. This is the
signal the model will use in Step 4. Your numbers may differ slightly in the second
decimal place.

## Checkpoint

<details>
<summary>Full <code>ask.py</code> after this step</summary>

```python
import json

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

collection = chromadb.PersistentClient(path=".chroma").get_collection("policies")

# Sources of every chunk the agent reads while answering one question.
retrieved = []


# ---------------------------------------------------------------------------
# The tools: ordinary Python functions the model is allowed to ask for.
# ---------------------------------------------------------------------------
def search_policies(query, document=None):
    embedding = client.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding
    result = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        where={"source": document} if document else None,
    )
    found = []
    for text, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        retrieved.append(f"{meta['source']} > {meta['section']}")
        # Cosine distance becomes a 0-to-1 relevance score the model can judge.
        found.append({"source": meta["source"], "section": meta["section"], "relevance": round(1 - distance, 2), "text": text})
    return json.dumps(found)
```

</details>

This file is not finished. Step 8 holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `InvalidCollectionException` or "Collection policies does not exist" | `ingest.py` has not been run in this folder | Run `uv run ingest.py` (Step 2) |
| `ModuleNotFoundError: No module named 'chromadb'` | The command ran without `uv run`, or `uv sync` was skipped | Run `uv sync` inside `hr-policy-qa-agentic`, and start Python with `uv run` |
| The score is a negative or a large number | The collection was made with a different distance setting | Delete `.chroma` and run `uv run ingest.py` again, which sets cosine distance |
| An empty list when a document is given | The name does not match the stored `source` exactly, for example `HR handbook` | Use the title as stored: `HR Handbook`. Step 4 makes the model pick from the exact list |

Next: **Step 4 — Describe the Tool and Let the Model Decide**.
