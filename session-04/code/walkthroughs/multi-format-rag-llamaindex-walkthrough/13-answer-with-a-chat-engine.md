# Step 13 — Answer With a Chat Engine

> Back to index · Previous: Hybrid Retrieval and Comparison · Next: Filter by File Type

## Goal

Write the first version of `ask.py`: a chat engine that uses the hybrid retriever, remembers
the conversation, and prints where each answer came from.

## Why this matters

Retrieval finds nodes. A chat engine turns them into an answer: it rewrites a follow-up
question as a full one, searches, puts the nodes and the question into a prompt, calls the
chat model and keeps the conversation. The earlier app got one by calling `as_chat_engine`
on the index, which builds its own vector retriever.

That shortcut no longer fits. We want our **own** retriever, the hybrid one, inside the
engine. So `ask.py` builds the engine directly, from the retriever, with
`CondensePlusContextChatEngine.from_defaults`. It is the same engine that `as_chat_engine`
made, with the retriever supplied by us.

Two consequences follow.

The first is that there is **no similarity cut-off** here. The cut-off from the earlier app
compared scores with 0.3, which suits similarities. The hybrid retriever's scores are rank
points around 0.01 to 0.03, so a cut-off of 0.3 would drop everything. When nothing relevant
exists, the system prompt carries the job: it tells the model to say it could not find the
answer and not to guess.

The second is the **memory**. It is created as a separate object, a `ChatMemoryBuffer`, and
handed to the engine. That looks like extra work now, and Step 14 explains why it pays off.

## 1. Create `ask.py`

Create `ask.py`:

```python
from dotenv import load_dotenv
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer

from retrieval import build_retrievers, configure_models, describe, open_index, open_nodes

load_dotenv()
configure_models()

SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "The context can come from a handbook, a PDF policy, spreadsheet rows, a checklist or an FAQ. "
    "If the answer needs facts from more than one source, combine them. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)

index = open_index()
nodes = open_nodes()

# The chat engine keeps the conversation in this memory object.
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

# Hybrid retrieval: vector search and keyword search, merged. See retrieval.py.
_, _, hybrid = build_retrievers(index, nodes)
chat_engine = CondensePlusContextChatEngine.from_defaults(
    retriever=hybrid, memory=memory, system_prompt=SYSTEM
)

print("Ask about company policies. Type 'reset' to forget the conversation, 'quit' to exit.\n")

while True:
    question = input("You: ").strip()

    if question.lower() in ("quit", "exit"):
        break
    if question.lower() == "reset":
        memory.reset()
        print("Conversation cleared.\n")
        continue

    response = chat_engine.chat(question)

    print("AI:", response)
    print("Retrieved from:")
    if not response.source_nodes:
        print("  - nothing found")
    for node in response.source_nodes:
        print(f"  - {describe(node.node)} (score {node.score:.3f})")
    print()
```

| Block | What it does |
|---|---|
| `load_dotenv()` and `configure_models()` | Reads the key and sets both models, as `ingest.py` does |
| `SYSTEM` | The instructions. It tells the model the context may come from five kinds of source, to combine facts from more than one, and to say "I could not find that in the policy documents" otherwise |
| `index = open_index()` and `nodes = open_nodes()` | The vector index from Chroma and the saved nodes for keyword search |
| `ChatMemoryBuffer.from_defaults(token_limit=3000)` | Remembers the conversation, up to about 3000 tokens, then forgets the oldest |
| `_, _, hybrid = build_retrievers(index, nodes)` | Takes only the third of the three retrievers |
| `CondensePlusContextChatEngine.from_defaults(...)` | The engine: rewrite, retrieve with `hybrid`, answer with `SYSTEM` and `memory` |
| `question = input(...).strip()` | `.strip()` so a stray space does not defeat a command |
| `reset` | `memory.reset()` clears the conversation |
| The last block | Prints the answer, then the sources |
| `describe(node.node)` | `source_nodes` are wrapped with a score. `.node` is the node inside, and `.score` is the fused score |

## Try it

```bash
uv run ask.py
```

Ask a question that needs one spreadsheet row:

```text
You: What is the hotel limit for an L3?
```

Expect an answer that gives 6,000 INR per night, followed by a source list that includes the
L3 row of the workbook, for example:

```text
Retrieved from:
  - expense_limits.xlsx > sheet Travel Limits, row 4 (score 0.033)
  - ...
```

Your wording and your scores will differ. The thing to check is that the L3 row is in the
list and that the number in the answer comes from it.

Then try a question that needs facts from two files:

```text
You: I am an L3 and my hotel cost 7000 INR a night. What happens?
```

A good answer says the limit is 6,000 INR (from the workbook) and that a stay above the limit
needs the department head's approval before booking, or the extra amount is recovered from the
employee (from the PDF). Check that both `expense_limits.xlsx` and `travel_policy.pdf` appear
in the sources. Then test the memory:

```text
You: And what about an L4?
```

The chat engine should rewrite this as a question about the L4 hotel limit, and answer 8,000
INR. Type `reset` and ask "And what about an L4?" again to see the memory gone.

## Checkpoint

<details>
<summary>Full <code>ask.py</code> after this step</summary>

```python
from dotenv import load_dotenv
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer

from retrieval import build_retrievers, configure_models, describe, open_index, open_nodes

load_dotenv()
configure_models()

SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "The context can come from a handbook, a PDF policy, spreadsheet rows, a checklist or an FAQ. "
    "If the answer needs facts from more than one source, combine them. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)

index = open_index()
nodes = open_nodes()

# The chat engine keeps the conversation in this memory object.
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

# Hybrid retrieval: vector search and keyword search, merged. See retrieval.py.
_, _, hybrid = build_retrievers(index, nodes)
chat_engine = CondensePlusContextChatEngine.from_defaults(
    retriever=hybrid, memory=memory, system_prompt=SYSTEM
)

print("Ask about company policies. Type 'reset' to forget the conversation, 'quit' to exit.\n")

while True:
    question = input("You: ").strip()

    if question.lower() in ("quit", "exit"):
        break
    if question.lower() == "reset":
        memory.reset()
        print("Conversation cleared.\n")
        continue

    response = chat_engine.chat(question)

    print("AI:", response)
    print("Retrieved from:")
    if not response.source_nodes:
        print("  - nothing found")
    for node in response.source_nodes:
        print(f"  - {describe(node.node)} (score {node.score:.3f})")
    print()
```

</details>

This file is not finished. Step 14 adds the file type filter.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: .store/docstore.json` | `ingest.py` was not run after Step 11 | Run `uv run ingest.py` |
| `ValueError: not enough values to unpack` | `build_retrievers` returns three retrievers, and the unpacking has a different count | Use `_, _, hybrid = build_retrievers(index, nodes)` |
| `AttributeError: 'NodeWithScore' object has no attribute 'metadata'` inside `describe` | `describe(node)` was called instead of `describe(node.node)` | Pass the inner node: `describe(node.node)` |
| Every answer is "I could not find that" | Ingest ran with different data, or the collection is empty | Re-run `ingest.py`, and check Step 9's count of 41 |
| A cut-off was added and everything disappears | A similarity cut-off of 0.3 was copied from the earlier app | Remove it. Fused scores are rank points |

Next: **Step 14 — Filter by File Type**.
