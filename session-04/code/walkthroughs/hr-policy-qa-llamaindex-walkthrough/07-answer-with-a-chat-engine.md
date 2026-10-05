# Step 7 — Answer with a Chat Engine

> Back to index · Previous: Open the Index and Retrieve · Next: Add the Similarity Cut-off

## Goal

Replace the retriever with a chat engine that retrieves, builds the prompt, calls
`gpt-4o-mini`, and remembers the conversation. Keep the hand-built system message word for
word.

## Why this matters

The hand-built app finished with a block you wrote yourself: join the chunks into
`context`, put a system message and a `Context: ... Question: ...` user message into a
list, and call the chat API. Every question was handled on its own, with no memory.

A **chat engine** wraps the whole of that, and adds the memory. You hand it a question. It
retrieves nodes, builds the prompt, calls the model, and keeps the conversation so far.

Memory solves a real problem. Ask "How many days of sick leave do I get?" and then "And
does it carry forward?". The second question, taken alone, says nothing about sick leave.
The hand-built app searched for those exact words and found whichever section was nearest
to them, which is very likely the carry-forward rule for **paid** leave: the wrong rule,
with a confident answer.

The chat mode used here, `condense_plus_context`, fixes that in three moves. It asks the
model to rewrite the follow-up using the conversation, "Does unused sick leave carry
forward?". It retrieves with the rewritten question. Then it answers with the retrieved
nodes in the prompt. The price is one extra model call for each follow-up question.

One thing to know about the prompt. The chat engine builds a single system message in
this order: a short preamble written by LlamaIndex, your retrieved nodes, an instruction
to answer from them, and then your own `SYSTEM` text. Your rules come last, which helps
them win. But the preamble is LlamaIndex's, and it describes the assistant as "talkative".
You are not in full control of the prompt any more. Exercise 4 in Step 9 shows you how
to read it.

## 1. Add the Chat Model

Add the import under the embedding import, and the setting under the embedding setting:

```python
from llama_index.llms.openai import OpenAI
```

```python
# The same embedding model as ingest.py, plus the chat model.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = OpenAI(model="gpt-4o-mini")
```

`Settings.llm` is to the chat model what `Settings.embed_model` is to the embedding model:
one place that says which model the whole program uses. It replaces the
`model="gpt-4o-mini"` in the hand-built chat call.

## 2. Add the System Message

Directly below the settings, add the same text as the hand-built app:

```python
SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)
```

## 3. Replace the Retriever with a Chat Engine

Delete the `retriever = ...` line. Below the line that makes the index, add:

```python
# Steps 5 and 6 in one object. A chat engine in this mode:
#   - rewrites a follow-up ("And does it carry forward?") into a full question,
#   - retrieves the 4 closest nodes,
#   - sends the nodes and the question to the model, and remembers the conversation.
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    similarity_top_k=4,
    system_prompt=SYSTEM,
)
```

| Argument | What it does |
|---|---|
| `chat_mode="condense_plus_context"` | Rewrite the follow-up, retrieve, then answer with the nodes as context. The other modes differ in how they do those steps, and Exercise 5 tries one |
| `similarity_top_k=4` | The same k as in Step 6. It is passed on to the retriever inside the engine |
| `system_prompt=SYSTEM` | Your rules, added to the prompt |

## 4. Ask Through the Engine

Change the welcome line, then replace the loop so that it also understands `reset`:

```python
print("Ask about company policies. Type 'reset' to forget the conversation, 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break
    if question.lower() == "reset":
        chat_engine.reset()
        print("Conversation cleared.\n")
        continue

    response = chat_engine.chat(question)

    print("AI:", response)
    print("Retrieved from:")
    for node in response.source_nodes:
        heading = node.text.splitlines()[0].lstrip("# ")
        print(f"  - {node.metadata['file_name']} > {heading} (score {node.score:.2f})")
    print()
```

| Part | What it does |
|---|---|
| `chat_engine.reset()` | Clears the memory. Without it, an old topic can colour the next question. It also lets you rerun a demo from a clean start |
| `chat_engine.chat(question)` | The whole of the hand-built Steps 7 and 8 in one call: retrieve, prompt, model |
| `print("AI:", response)` | The response prints as its answer text |
| `response.source_nodes` | The nodes the answer was built from, each with its score. This is the "Retrieved from" list, now fed from the response and not from a separate query |

## Try it

```bash
uv run ask.py
```

Ask a follow-up pair:

```text
You: How many days of sick leave do I get?
AI: (8 days a year, separate from paid leave)
Retrieved from:
  - 02_leave_policy.md > Sick Leave (score 0.xx)
  - (three more lines)

You: And does it carry forward?
AI: (no: unused sick leave does not carry forward and cannot be encashed)
Retrieved from:
  - 02_leave_policy.md > Sick Leave (score 0.xx)
  - (three more lines)

You: reset
Conversation cleared.

You: And does it carry forward?
AI: (a different answer, or "I could not find that in the policy documents.")
Retrieved from:
  - (four lines that no longer centre on sick leave)

You: quit
```

The text in brackets stands for the model's own wording, which differs from run to run.
What matters is the pattern. The second question is answered about sick leave because the
engine remembered the first. After `reset`, the same words mean nothing, and the answer
changes.

Now run the same first two questions in the hand-built app, in a second terminal:

```bash
cd ../hr-policy-qa
uv run ask.py
```

It has no memory, so the follow-up is searched for as written. Compare what is under
"Retrieved from" in the two apps.

Last, ask "What is the capital of France?" in the new app. Four nodes come back, as
before, and the instruction in `SYSTEM` is the only thing that stops the model from using
them. Step 8 adds a second safeguard.

## Checkpoint

<details>
<summary>Full <code>ask.py</code> after this step</summary>

```python
import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

# The same embedding model as ingest.py, plus the chat model.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = OpenAI(model="gpt-4o-mini")

SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)

# Open the Chroma collection that ingest.py filled, and wrap it as an index.
collection = chromadb.PersistentClient(path=".chroma").get_collection("policies_llamaindex")
index = VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))

# Steps 5 and 6 in one object. A chat engine in this mode:
#   - rewrites a follow-up ("And does it carry forward?") into a full question,
#   - retrieves the 4 closest nodes,
#   - sends the nodes and the question to the model, and remembers the conversation.
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    similarity_top_k=4,
    system_prompt=SYSTEM,
)

print("Ask about company policies. Type 'reset' to forget the conversation, 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break
    if question.lower() == "reset":
        chat_engine.reset()
        print("Conversation cleared.\n")
        continue

    response = chat_engine.chat(question)

    print("AI:", response)
    print("Retrieved from:")
    for node in response.source_nodes:
        heading = node.text.splitlines()[0].lstrip("# ")
        print(f"  - {node.metadata['file_name']} > {heading} (score {node.score:.2f})")
    print()
```

</details>

This file is not finished. Step 8 adds the similarity cut-off and holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ValueError` or an error about `chat_mode` | The mode name is misspelt | It is exactly `condense_plus_context`, with underscores |
| The follow-up is answered about the wrong policy | `reset` was typed before it, or the program was restarted | Memory lives only while the program runs. Ask the first question again |
| `AuthenticationError` mid-session | Key problem, as in Step 5 | Check `.env` |
| Every answer is "I could not find that in the policy documents." | The collection is empty or from a failed ingest | Run `uv run ingest.py` and check that it reports 46 |
| An answer includes extra detail the policy does not state | LlamaIndex's own preamble nudges the model to be talkative | Check "Retrieved from" first. See Exercise 4 in Step 9 |

Next: **Step 8 — Add the Similarity Cut-off**.
