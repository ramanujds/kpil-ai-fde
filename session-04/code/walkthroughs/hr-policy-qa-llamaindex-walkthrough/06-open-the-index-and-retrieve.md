# Step 6 — Open the Index and Retrieve

> Back to index · Previous: Embed and Store with an Index · Next: Answer with a Chat Engine

## Goal

Start the new `ask.py`: open the index that `ingest.py` built, turn a question into the
four closest nodes, and print each one with a score. The chat model is not involved yet.

## Why this matters

As in the hand-built walkthrough, this step stops before the model on purpose. Retrieval
decides whether a correct answer is possible, so you want to judge it on its own, before
the model's wording gets mixed in.

The hand-built `ask.py` did three things here: create a client, embed the question, and
call `collection.query(...)`. A **retriever** does all three. You give it the question; it
embeds it with the embedding model from `Settings`, searches the store, and returns the
closest nodes.

What it returns is also richer. Each result is a node together with a **score**, a number
saying how close that node is to the question. The hand-built query returned distances,
where smaller meant closer. LlamaIndex turns that around into a similarity, where **bigger
means closer**, which is easier to read. A value of 1 would mean the same direction.

The scores are the real reason to do this step carefully. Retrieval always returns four
nodes, even for a question the documents do not cover. What separates a good match from a
poor one is the score, and Step 8 uses it. So while you test here, **write down the
scores**.

## 1. Open the Index

Delete everything in `ask.py`, then write:

```python
import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

# The same embedding model as ingest.py.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Open the Chroma collection that ingest.py filled, and wrap it as an index.
collection = chromadb.PersistentClient(path=".chroma").get_collection("policies_llamaindex")
index = VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))
```

| Part | What it does |
|---|---|
| `Settings.embed_model = ...` | The same model as in `ingest.py`. The question must be embedded the same way as the nodes |
| `get_collection("policies_llamaindex")` | Opens the collection the new `ingest.py` made. It raises an error if the collection does not exist, which is right: there is nothing to search before ingest has run |
| `VectorStoreIndex.from_vector_store(...)` | Wraps an existing store as an index. Compare with `VectorStoreIndex(nodes, ...)` in `ingest.py`, which builds a store from nodes. This one embeds nothing |

## 2. Make a Retriever and Ask

```python
retriever = index.as_retriever(similarity_top_k=4)

print("Ask about company policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    results = retriever.retrieve(question)
```

`similarity_top_k=4` is the k of top-k, the same number the hand-built code called
`n_results`. `retriever.retrieve(question)` returns a list of four results, closest first.

## 3. Show What Came Back

Inside the loop, after the retrieve line:

```python
    print(results[0].text)
    print("Retrieved from:")
    for node in results:
        heading = node.text.splitlines()[0].lstrip("# ")
        print(f"  - {node.metadata['file_name']} > {heading} (score {node.score:.2f})")
    print()
```

| Part | What it does |
|---|---|
| `results[0].text` | The text of the closest node. This line is only for looking. Step 7 replaces it |
| `node.text.splitlines()[0]` | The first line of the node, which is its `## Heading` |
| `.lstrip("# ")` | Removes the leading `#` characters and the space, as in the hand-built chunking |
| `node.metadata['file_name']` | The file name that Step 3 chose to keep |
| `node.score` | The similarity, shown to two decimals |

## Try it

```bash
uv run ask.py
```

Ask a question that shares almost no important word with the document, as in the
hand-built walkthrough:

```text
You: Can I roll over my vacation days?
## Carry Forward of Leave
Unused paid leave of up to 6 days carries forward to the next leave year. ...
Retrieved from:
  - 02_leave_policy.md > Carry Forward of Leave (score 0.xx)
  - (three more lines, with lower scores)

You: What is the capital of France?
## Accessories
...
Retrieved from:
  - (four lines, none of them about France)

You: quit
```

Your scores and the order of the lower lines will differ, so `0.xx` stands for a number you
will read off your own screen. What to look for:

| Check | What you should see |
|---|---|
| The vacation question | Carry Forward of Leave comes first, as it did in the hand-built app. This is search by meaning, now with a score |
| The France question | Four nodes still come back, with no relevant one among them, as before |
| The scores | The first score for the vacation question should be noticeably higher than the first score for the France question. If it is not, tell your trainer: that gap is what Step 8 relies on |

Now do the exercise that Step 8 depends on. Ask three questions that the documents answer,
and then the France question. For each, write down the **top score** and the **fourth
score**. Keep the page.

## Checkpoint

<details>
<summary>Full <code>ask.py</code> after this step</summary>

```python
import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

# The same embedding model as ingest.py.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Open the Chroma collection that ingest.py filled, and wrap it as an index.
collection = chromadb.PersistentClient(path=".chroma").get_collection("policies_llamaindex")
index = VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))

retriever = index.as_retriever(similarity_top_k=4)

print("Ask about company policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    results = retriever.retrieve(question)

    print(results[0].text)
    print("Retrieved from:")
    for node in results:
        heading = node.text.splitlines()[0].lstrip("# ")
        print(f"  - {node.metadata['file_name']} > {heading} (score {node.score:.2f})")
    print()
```

</details>

This file is not finished. Steps 7 and 8 change it, and Step 8 holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `NotFoundError: Collection [policies_llamaindex] does not exist` | `ingest.py` has not been run, or it ran in a different folder, so a `.chroma` store was created elsewhere | Run `uv run ingest.py` from the same folder as `ask.py` |
| `Collection expecting embedding with dimension of 1536, got ...` | The question was embedded with a different model from the nodes | Use the same model name in both files |
| `KeyError: 'file_name'` | The nodes were stored without that metadata, for example by an older `ingest.py` | Re-check Step 3, then delete `.chroma` and run `ingest.py` again |
| `AuthenticationError` on the first question | The key is missing, as in Step 5 | Check `.env` |

Next: **Step 7 — Answer with a Chat Engine**.
