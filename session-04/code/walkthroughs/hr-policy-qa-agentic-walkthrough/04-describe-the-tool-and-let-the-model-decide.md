# Step 4 — Describe the Tool and Let the Model Decide

> Back to index · Previous: The Search Tool · Next: Run the Tool and Return the Result

## Goal

Tell the model that `search_policies` exists, give it the rules for using it, and print the
model's decision for a few questions without running anything.

## Why this matters

The model cannot see your Python. It never reads `search_policies`, and it cannot import
it. All it knows about a tool is what you write in the **tool description**: a name, a
sentence about what it does, and the arguments it takes. Everything the model decides about
the tool, it decides from that text. So the description is not documentation. It is part of
the program.

When the model decides to use a tool, it does not run anything. It replies with a request:
"call `search_policies` with `query` = 'notice period' and `document` = 'HR Handbook'".
Your code is the one that runs it. That is the most important idea in this walkthrough,
and this step shows it in isolation: you will see the model's request and do nothing with
it.

Looking at the raw decision before acting on it pays off. It shows what the model chose, in
what words, and sometimes that it chose wrong. Which way it can go wrong is worth seeing
now:

| The model decides... | Right when | Wrong when |
|---|---|---|
| To call the tool | The question is about a policy | The user only said hello |
| Not to call the tool | It is small talk | It is a policy question, and the model answers from memory |
| To search one document | The question names one topic | The answer lives in two documents |

## 1. List the Documents

The model will be offered a fixed list of document names to choose from, instead of typing
a name freely. Below the line that opens the collection, add:

```python

# The document names in the store, so the agent can search one document at a time.
documents = sorted({m["source"] for m in collection.get(include=["metadatas"])["metadatas"]})
```

This reads every chunk's `source` from Chroma and keeps the distinct ones. If you add a
seventh document and run `ingest.py`, the list updates by itself.

## 2. Write the Rules

Below it, add the system message:

```python

SYSTEM = (
    "You answer questions about company policies. You have one tool: search_policies.\n"
    "- Never state a policy fact from memory. Use ONLY text returned by search_policies.\n"
    "- If a question has several parts, or spans several documents, search for each part "
    "separately.\n"
    "- If the results look weak or off-topic, rewrite the query or try another document "
    "before giving up.\n"
    "- For greetings and small talk, answer directly without any tool.\n"
    "- Cite every fact as [Document > Section]. If the answer is not in the documents, "
    "say 'I could not find that in the policy documents.' Do not guess."
)
```

Compare it with the hand-built system message. That one said only what to do with the
context it was handed. This one has to say **how to work**, because the model now controls
the work:

| Rule | What behaviour it is meant to produce |
|---|---|
| Never state a policy fact from memory | Stops answers that sound right but come from nowhere |
| Search for each part separately | Multi-part and comparison questions get one search per part |
| Rewrite or try another document when results are weak | The retry, driven by the relevance score |
| Greetings need no tool | No pointless search for "thanks" |
| Cite as `[Document > Section]` | The source of every fact is visible, as in Block 6 |

## 3. Describe the Tool

Below the `search_policies` function, add the registry and the description:

```python


TOOL_FUNCTIONS = {"search_policies": search_policies}

# What the model sees: a name, a description and the arguments for each tool.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_policies",
            "description": (
                "Search the company policy documents and return the 3 most relevant sections. "
                "Each result has a relevance score from 0 to 1; below about 0.3 usually means "
                "the text is not about the question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "A complete, standalone search query."},
                    "document": {
                        "type": "string",
                        "enum": documents,
                        "description": "Optional. Search only this document.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]
```

| Part | What it does |
|---|---|
| `TOOL_FUNCTIONS` | Your side only: a lookup from the name the model uses to the real function. The model never sees it. Step 5 uses it |
| `"name"` | The name the model will use in its request. It must match the key in `TOOL_FUNCTIONS` |
| `"description"` | The model's only source of understanding. It also explains the scores, so the model can read "0.09" as a failed search |
| `"query"` | "A complete, standalone search query" pushes the model to write a full query rather than a fragment like "and carry forward" |
| `"enum": documents` | The model can only choose one of the real document names. A typo is impossible, which avoids the empty result you saw as a common mistake in Step 3 |
| `"required": ["query"]` | `document` is optional, so a search of everything is still possible |

## 4. Show the Decision

Add a small loop at the bottom that sends the question to the model and prints what comes
back. It does not run any tool.

```python
print("Ask about company policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    reply = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS).choices[0].message

    # Only look at the decision. Nothing is run yet.
    if reply.tool_calls:
        for call in reply.tool_calls:
            print(f"The model wants: {call.function.name}({call.function.arguments})")
    else:
        print("The model answered directly:", reply.content)
    print()
```

| Part | What it does |
|---|---|
| `tools=TOOLS` | The one new argument compared with the hand-built chat call. It hands the model the descriptions |
| `.choices[0].message` | The model's reply. It carries either `content` (an answer) or `tool_calls` (requests), and normally not both |
| `call.function.arguments` | The arguments the model chose, as a JSON **string**. Step 5 parses it |

## Try it

```bash
uv run ask.py
```

```text
Ask about company policies. Type 'quit' to exit.

You: Hi, thanks!
The model answered directly: You're welcome! How can I assist you today?

You: How long is the notice period?
The model wants: search_policies({"query":"notice period","document":"HR Handbook"})

You: Compare the leave policy and the work from home policy on manager approval.
The model wants: search_policies({"query": "manager approval", "document": "Leave Policy"})
The model wants: search_policies({"query": "manager approval", "document": "Work From Home Policy"})

You: What is the capital of France?
The model answered directly: The capital of France is Paris.

You: quit
```

Read each decision. A greeting gets no search. The notice period question goes to the HR
Handbook only, which is where it lives. The comparison question produces **two** requests,
one per document, which the hand-built app could never do.

The last answer is a flaw. The model answered a general-knowledge question from memory,
and nothing in the rules told it not to. Keep it in mind. Step 6 fixes it with one line.

The exact arguments, including spacing and wording, can differ on your machine.

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

# The document names in the store, so the agent can search one document at a time.
documents = sorted({m["source"] for m in collection.get(include=["metadatas"])["metadatas"]})

SYSTEM = (
    "You answer questions about company policies. You have one tool: search_policies.\n"
    "- Never state a policy fact from memory. Use ONLY text returned by search_policies.\n"
    "- If a question has several parts, or spans several documents, search for each part "
    "separately.\n"
    "- If the results look weak or off-topic, rewrite the query or try another document "
    "before giving up.\n"
    "- For greetings and small talk, answer directly without any tool.\n"
    "- Cite every fact as [Document > Section]. If the answer is not in the documents, "
    "say 'I could not find that in the policy documents.' Do not guess."
)

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


TOOL_FUNCTIONS = {"search_policies": search_policies}

# What the model sees: a name, a description and the arguments for each tool.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_policies",
            "description": (
                "Search the company policy documents and return the 3 most relevant sections. "
                "Each result has a relevance score from 0 to 1; below about 0.3 usually means "
                "the text is not about the question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "A complete, standalone search query."},
                    "document": {
                        "type": "string",
                        "enum": documents,
                        "description": "Optional. Search only this document.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

print("Ask about company policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    reply = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS).choices[0].message

    # Only look at the decision. Nothing is run yet.
    if reply.tool_calls:
        for call in reply.tool_calls:
            print(f"The model wants: {call.function.name}({call.function.arguments})")
    else:
        print("The model answered directly:", reply.content)
    print()
```

</details>

This file is not finished. Step 8 holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Invalid schema for function 'search_policies'` | A bracket is misplaced in `TOOLS`, or `"type": "object"` is missing | Compare `TOOLS` with the checkpoint, one level at a time |
| The model never calls the tool, even for policy questions | `tools=TOOLS` is missing from the call, or the `description` is vague | Check the call, then make the description say plainly what the tool is for |
| `enum` must have at least one item | `documents` is empty because `ingest.py` was not run | Run `uv run ingest.py` |
| `TypeError: 'NoneType' object is not iterable` | Code tried to loop over `reply.tool_calls` without checking it first. It is `None` when the model answers directly | Keep the `if reply.tool_calls:` check |

Next: **Step 5 — Run the Tool and Return the Result**.
