# Step 14 — Filter by File Type

> Back to index · Previous: Answer With a Chat Engine · Next: Recap and Exercises

## Goal

Add a `/only` command to `ask.py` that restricts both searches to one file type, without the
assistant forgetting the conversation.

## Why this matters

Sometimes the user knows where the answer is: "it's in the PDF." Letting them say so removes
every other file's nodes from the competition, and is also the clearest way to see the
filter working, because the source list changes at once.

The command changes the retriever, and the retriever is inside the chat engine. So the
engine has to be **rebuilt** with a new retriever each time the filter changes. If the
conversation lived inside the engine, rebuilding it would wipe the conversation, and the
user who typed `/only pdf` would find the assistant had forgotten the last five questions.

That is why the memory was made as a separate object in Step 13. It outlives every engine.
`make_engine` creates a new engine around the same `memory`, so the filter changes and the
conversation continues.

## 1. Wrap the Engine in a Function

Change the comment above `memory`, then replace the block that built the engine with a
function and a first call. First the comment:

```python
# One memory object that outlives the engine, so changing the file type filter
# does not make the assistant forget the conversation.
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
```

Then replace the engine-building lines with:

```python
def make_engine(file_type):
    # Hybrid retrieval: vector search and keyword search, merged. See retrieval.py.
    _, _, hybrid = build_retrievers(index, nodes, file_type=file_type)
    return CondensePlusContextChatEngine.from_defaults(
        retriever=hybrid, memory=memory, system_prompt=SYSTEM
    )


file_type = None
chat_engine = make_engine(file_type)
```

`file_type=None` means "no filter", which `build_retrievers` already understands.

## 2. Update the Opening Message

Replace the single `print` before the loop with three:

```python
print("Ask about company policies.")
print("Commands: /only pdf|xlsx|md|docx|csv  search one file type    /only all  search everything")
print("          reset  forget the conversation    quit  exit\n")
```

## 3. Handle the Command

Inside the loop, after the `reset` block and before the `chat` call, add:

```python
    if question.lower().startswith("/only"):
        choice = question[5:].strip().lower()
        file_type = None if choice in ("", "all") else choice
        chat_engine = make_engine(file_type)
        print(f"Searching {file_type or 'all file types'}.\n")
        continue
```

| Line | What it does |
|---|---|
| `question[5:]` | Everything after the five characters of `/only` |
| `file_type = None if choice in ("", "all") else choice` | `/only all`, or `/only` alone, turns the filter off |
| `make_engine(file_type)` | A new engine with a retriever limited to that type, around the same memory |
| `continue` | Goes back to the prompt, so the command is not sent to the model as a question |

## Try it

```bash
uv run ask.py
```

```text
Ask about company policies.
Commands: /only pdf|xlsx|md|docx|csv  search one file type    /only all  search everything
          reset  forget the conversation    quit  exit

You: What is the hotel limit for an L3?
```

Note the answer and the sources. Now narrow to the PDF and ask again:

```text
You: /only pdf
Searching pdf.

You: What is the hotel limit for an L3?
```

Every line in the source list should now name `travel_policy.pdf`, with a page number. The
limit is in the workbook, not in the PDF (the PDF only says it "depends on grade"), so the
assistant should say it could not find the figure. Then:

```text
You: /only xlsx
Searching xlsx.

You: And for an L4?
```

The follow-up still works, because the memory survived two engine changes. The sources should
name only `expense_limits.xlsx`. Finally, `/only all` returns to searching everything.

## Checkpoint

<details>
<summary>Full <code>ask.py</code></summary>

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

# One memory object that outlives the engine, so changing the file type filter
# does not make the assistant forget the conversation.
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)


def make_engine(file_type):
    # Hybrid retrieval: vector search and keyword search, merged. See retrieval.py.
    _, _, hybrid = build_retrievers(index, nodes, file_type=file_type)
    return CondensePlusContextChatEngine.from_defaults(
        retriever=hybrid, memory=memory, system_prompt=SYSTEM
    )


file_type = None
chat_engine = make_engine(file_type)

print("Ask about company policies.")
print("Commands: /only pdf|xlsx|md|docx|csv  search one file type    /only all  search everything")
print("          reset  forget the conversation    quit  exit\n")

while True:
    question = input("You: ").strip()

    if question.lower() in ("quit", "exit"):
        break
    if question.lower() == "reset":
        memory.reset()
        print("Conversation cleared.\n")
        continue
    if question.lower().startswith("/only"):
        choice = question[5:].strip().lower()
        file_type = None if choice in ("", "all") else choice
        chat_engine = make_engine(file_type)
        print(f"Searching {file_type or 'all file types'}.\n")
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

This matches the reference project's `ask.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `/only pdf` is sent to the model as a question | The command block is placed after the `chat` call, or `continue` is missing | Put it before `response = chat_engine.chat(question)`, and end it with `continue` |
| The assistant forgets the conversation after `/only` | The memory was created inside `make_engine`, so each engine got a new one | Create `memory` once, outside the function |
| `/only PDF` finds nothing | The value is not lower-cased | `.lower()`, as shown. The stored type is `pdf` |
| `/only txt` returns no sources | There is no such file type in the collection | Use one of the five types. An unknown type gives an empty list, by design |
| The filter seems to have no effect | `make_engine(file_type)` was called but the result was not stored in `chat_engine` | Assign it: `chat_engine = make_engine(file_type)` |

Next: **Step 15 — Recap and Exercises**.
