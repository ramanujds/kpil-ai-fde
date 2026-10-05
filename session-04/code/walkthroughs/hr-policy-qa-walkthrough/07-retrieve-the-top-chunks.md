# Step 7 — Retrieve the Top Chunks

> Back to index · Previous: Store the Vectors · Next: Answer with the Model

## Goal

Start `ask.py`: read a question, turn it into a vector, and fetch the four stored chunks
closest in meaning. The chat model is not involved yet.

## Why this matters

Retrieval is the half of RAG that decides whether the final answer can be right. The model
can only work with what it is handed. If the right section is not among the four chunks,
no prompt, however well written, will rescue the answer.

That is why this step stops before the model. Seeing the retrieved chunks on their own
lets you judge retrieval separately from generation. When an answer is wrong later, the
first thing to ask is: was the right chunk retrieved? If not, the fix lies in chunking,
embeddings or the number of chunks. If yes, the fix lies in the prompt or the model.

The question must be embedded with the same model that embedded the chunks. The vectors then
live on the same map, and "closest" means something.

## 1. Open the Store and Create the Client

Create `ask.py`:

```python
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

collection = chromadb.PersistentClient(path=".chroma").get_collection("policies")
```

This opens the store that `ingest.py` built. `get_collection` raises an error if the
collection does not exist, which is the right behaviour: there is nothing to search until
`ingest.py` has run.

## 2. The Question Loop

The loop is the same one as in `simple-chat`:

```python
print("Ask about company policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break
```

## 3. Embed the Question and Query the Store

Inside the loop, after the quit check:

```python
    # Step 5: turn the question into a vector (same model as ingest.py), then
    # fetch the 4 stored chunks whose vectors are closest to it.
    response = client.embeddings.create(model="text-embedding-3-small", input=question)
    result = collection.query(query_embeddings=[response.data[0].embedding], n_results=4)
    chunks = result["documents"][0]
```

| Part | What it does |
|---|---|
| `input=question` | Embeds one text instead of a list, so `response.data` has one item |
| `query_embeddings=[...]` | Chroma accepts several questions at once, so the vector is wrapped in a list |
| `n_results=4` | The k in top-k: how many chunks to return |
| `result["documents"][0]` | The texts for the first (and only) question, closest first |

`result` also holds `metadatas` and `distances`, laid out the same way: a list with one
entry per question, and inside it one entry per returned chunk.

## 4. Show What Came Back

For now, print the best chunk and the list of where the four chunks came from:

```python
    print(chunks[0])
    print("Retrieved from:")
    for meta in result["metadatas"][0]:
        print(f"  - {meta['source']} > {meta['section']}")
    print()
```

The first line is only for looking. You will replace it in Step 8.

## Try it

```bash
uv run ask.py
```

Ask a question that shares almost no important word with the document:

```text
You: Can I roll over my vacation days?
Leave Policy > Carry Forward of Leave
Unused paid leave of up to 6 days carries forward to the next leave year. Leave beyond 6 days expires on 31 March. This does not apply to employees in their first year of service, who cannot carry forward any leave. Carried-forward leave must be used by 30 June of the new year.
Retrieved from:
  - Leave Policy > Carry Forward of Leave
  - Leave Policy > Sick Leave
  - Leave Policy > Leave Without Pay
  - Leave Policy > How to Apply for Leave

You: What is the capital of France?
Laptop and Equipment Policy > Accessories
A mouse, keyboard and headset are provided on request through the service desk. External monitors are available at the office only. Employees working from home may request an external monitor once, if their manager approves.
Retrieved from:
  - Laptop and Equipment Policy > Accessories
  - IT Security Policy > Passwords
  - Expense Reimbursement Policy > Travel Limits
  - Expense Reimbursement Policy > Meal Allowance

You: quit
```

The words "roll over" and "vacation" appear nowhere in the leave policy, yet the right
section comes first. That is search by meaning. The France question shows the other side:
the store always returns four chunks, even when none of them is relevant. It does not know
the question is off-topic. Step 8 handles that.

Your lower-ranked chunks may come back in a slightly different order.

## Checkpoint

<details>
<summary>Full <code>ask.py</code> after this step</summary>

```python
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

collection = chromadb.PersistentClient(path=".chroma").get_collection("policies")

print("Ask about company policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    # Step 5: turn the question into a vector (same model as ingest.py), then
    # fetch the 4 stored chunks whose vectors are closest to it.
    response = client.embeddings.create(model="text-embedding-3-small", input=question)
    result = collection.query(query_embeddings=[response.data[0].embedding], n_results=4)
    chunks = result["documents"][0]

    print(chunks[0])
    print("Retrieved from:")
    for meta in result["metadatas"][0]:
        print(f"  - {meta['source']} > {meta['section']}")
    print()
```

</details>

This file is not finished. Step 8 adds the model call and holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `NotFoundError: Collection [policies] does not exist` | `ingest.py` has not been run, or it was run from a different folder, so a `.chroma` store was created elsewhere | Run `uv run ingest.py` from the same folder as `ask.py` |
| `Collection expecting embedding with dimension of 1536, got ...` | The question was embedded with a different model from the chunks | Use the same model name in both files |
| The wrong section comes first | The answer is not in a chunk of its own, or the chunk is too vague to match | Look at the chunk text; chunking and wording are the usual causes, not the code |
| Fewer than 4 chunks come back | The store holds fewer than 4 chunks | Re-run `ingest.py` and check that it reports 40 |

Next: **Step 8 — Answer with the Model**.
