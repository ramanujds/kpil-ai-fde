# Step 8 — Handle Failures

> Back to index · Previous: A Second Tool, Who Is Asking · Next: Recap and Exercises

## Goal

Make the agent survive its own mistakes: a tool call that cannot be run goes back to the
model as text so it can recover, and a failed model call (rate limit, wrong key, no network)
prints a message and leaves the session usable.

## Why this matters

A pipeline has few ways to fail. An agent has many more, because the model writes part of
the program's input. Two kinds of failure matter here, and they need opposite handling.

| Failure | Whose fault | Right response |
|---|---|---|
| The model asks for a tool that does not exist, or sends malformed or wrong arguments | The model's. It is a mistake in its request | Tell **the model**, as a tool result, what went wrong, so it can correct itself |
| The API call itself fails: rate limit, wrong key, no network | Neither. It is the environment | Tell **the user**, and put the session back as it was |

The first kind must not crash the program. A model that sends `{"query": }` (invalid JSON)
or asks for `search_policy` instead of `search_policies` has only made a typo. If the error
is handed back as a normal tool result, the model usually reads it and tries again.

The second kind needs one more piece of care. Look at what the history contains halfway
through a question: an assistant message that asks for tools, perhaps with some results
added. If the call fails at that point, the history ends with a request that has no result.
The next question would then be rejected by the API (the rule from Step 5), and every
question after it. Cutting the history back to where it stood before the question started
keeps the session healthy.

Free-tier keys hit rate limits quickly, and the agent makes several calls per question, so
this is not a rare case.

## 1. Import the Error Type

Change the OpenAI import:

```python
from openai import OpenAI, OpenAIError
```

`OpenAIError` is the base class for every error the library raises, including rate limits,
bad keys and connection failures.

## 2. Protect `run_tool`

Replace `run_tool` with:

```python
def run_tool(call):
    """Run one tool the model asked for. A mistake goes back to the model as text instead of crashing."""
    name = call.function.name
    try:
        args = json.loads(call.function.arguments or "{}")
        shown = ", ".join(f"{key}={value!r}" for key, value in args.items())
        print(f"  -> {name}({shown})")
        return TOOL_FUNCTIONS[name](**args)
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"  -> {name} failed: {error!r}")
        return json.dumps({"error": f"Could not run {name}: {error!r}"})
```

| Exception | When it happens |
|---|---|
| `json.JSONDecodeError` | The arguments are not valid JSON |
| `KeyError` | The tool name is not in `TOOL_FUNCTIONS` |
| `TypeError` | The arguments do not fit the function, for example an extra or missing one |

The result is still a JSON string with an `error` field, so the rest of the loop is
unchanged. The model gets a normal tool result that happens to say what went wrong.

## 3. Protect the Question Loop

In the loop at the bottom, record where the history stands, and wrap the call:

```python
    checkpoint = len(messages)
    retrieved.clear()
    messages.append({"role": "user", "content": question})

    try:
        answer = run_agent(messages)
    except OpenAIError as error:  # rate limit, bad key, network
        del messages[checkpoint:]  # drop the half-finished turn so the next question starts clean
        print(f"The model call failed: {error}\n")
        continue

    print("AI:", answer)
```

| Part | What it does |
|---|---|
| `checkpoint = len(messages)` | Remembers how long the history was before this question |
| `del messages[checkpoint:]` | Removes the question and everything the agent added since, including any unanswered tool request |
| `continue` | Goes back to the prompt, so the user can try again or quit |

## Try it

First, break the tool registry on purpose. In `TOOL_FUNCTIONS`, change the key
`"search_policies"` to `"search"`, and ask a question:

```text
You: How long is the notice period?
  -> search_policies(query='notice period', document='HR Handbook')
  -> search_policies failed: KeyError('search_policies')
  -> search_policies(query='notice period', document='HR Handbook')
  -> search_policies failed: KeyError('search_policies')
  -> search_policies(query='notice period')
  -> search_policies failed: KeyError('search_policies')
AI: I could not find that in the policy documents.
```

The program did not crash. The model was told each time, tried again, once without the
document filter, and then gave up with the honest answer from its rules. Change the key back
to `"search_policies"`.

Now break the key. Run with a wrong value, which takes priority over the `.env` file:

```bash
OPENAI_API_KEY=sk-wrong uv run ask.py
```

```text
You: hello
The model call failed: Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-wrong. ...
```

The message is shown, and the prompt comes back. Nothing crashed. With the right key,
everything works again.

Last, check that the session recovers. Ask a question normally, a follow-up, and then a
third. The history was never left with a request that had no result, so the follow-ups
still work.

## Checkpoint

<details>
<summary>Full <code>ask.py</code></summary>

```python
import json
from datetime import date
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()
client = OpenAI()

MAX_STEPS = 5  # the most tool rounds the agent gets for one question

collection = chromadb.PersistentClient(path=".chroma").get_collection("policies")
employees = json.loads(Path("employees.json").read_text())

# The document names in the store, so the agent can search one document at a time.
documents = sorted({m["source"] for m in collection.get(include=["metadatas"])["metadatas"]})

SYSTEM = (
    "You answer questions about company policies. You have two tools: search_policies "
    "and get_my_profile.\n"
    "- Never state a policy fact from memory. Use ONLY text returned by search_policies.\n"
    "- If a question has several parts, or spans several documents, search for each part "
    "separately.\n"
    "- If the results look weak or off-topic, rewrite the query or try another document "
    "before giving up.\n"
    "- If the answer depends on the user's own situation (probation, first year, level, "
    "notice period, leave earned so far), call get_my_profile FIRST. Then search for the "
    "rule that applies to that situation. Never ask the user for facts the profile has.\n"
    "- For greetings and small talk, answer directly without any tool.\n"
    "- You only answer company policy questions. For anything else, including general "
    "knowledge, do not answer it.\n"
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


def get_my_profile():
    # Only the signed-in user's own record is ever returned. The model cannot ask for anyone else's.
    joined = date.fromisoformat(me["joined"])
    today = date.today()
    months = (today.year - joined.year) * 12 + today.month - joined.month - (today.day < joined.day)
    return json.dumps({**me, "months_of_service": months, "today": today.isoformat()})


TOOL_FUNCTIONS = {"search_policies": search_policies, "get_my_profile": get_my_profile}

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
    {
        "type": "function",
        "function": {
            "name": "get_my_profile",
            "description": "Get the signed-in employee's name, role, level, department, joining date and months of service.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def run_tool(call):
    """Run one tool the model asked for. A mistake goes back to the model as text instead of crashing."""
    name = call.function.name
    try:
        args = json.loads(call.function.arguments or "{}")
        shown = ", ".join(f"{key}={value!r}" for key, value in args.items())
        print(f"  -> {name}({shown})")
        return TOOL_FUNCTIONS[name](**args)
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"  -> {name} failed: {error!r}")
        return json.dumps({"error": f"Could not run {name}: {error!r}"})


# ---------------------------------------------------------------------------
# The agent loop: ask the model, run the tools it requests, repeat until it answers.
# ---------------------------------------------------------------------------
def run_agent(messages):
    for _ in range(MAX_STEPS):
        reply = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS).choices[0].message
        messages.append(reply)

        if not reply.tool_calls:  # no tool requested: this is the final answer
            return reply.content

        for call in reply.tool_calls:
            messages.append({"role": "tool", "tool_call_id": call.id, "content": run_tool(call)})

    # Step cap reached: stop the searching and make the model answer with what it has.
    print(f"  (step limit of {MAX_STEPS} reached)")
    messages.append({"role": "user", "content": "Stop searching. Answer now from what you have found, or say you could not find it."})
    reply = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS, tool_choice="none").choices[0].message
    messages.append(reply)
    return reply.content


employee_id = input("Your employee ID (for example E101): ").strip().upper()
if employee_id not in employees:
    raise SystemExit(f"Unknown employee ID. Try one of: {', '.join(employees)}")
me = employees[employee_id]

print(f"\nHello {me['name']}. Ask about company policies. Type 'quit' to exit.\n")

# The history is kept between questions, so a follow-up like "and does it carry forward?" still makes sense.
messages = [{"role": "system", "content": SYSTEM}]

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    checkpoint = len(messages)
    retrieved.clear()
    messages.append({"role": "user", "content": question})

    try:
        answer = run_agent(messages)
    except OpenAIError as error:  # rate limit, bad key, network
        del messages[checkpoint:]  # drop the half-finished turn so the next question starts clean
        print(f"The model call failed: {error}\n")
        continue

    print("AI:", answer)
    if retrieved:
        print("Retrieved from:")
        for source in dict.fromkeys(retrieved):  # unique, in the order they were read
            print(f"  - {source}")
    print()
```

</details>

This matches the reference project's `ask.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| A rate-limit error crashes the program with a traceback | The `except OpenAIError` is missing, or `run_agent` is called outside the `try` | Put the call to `run_agent` inside the `try`, as shown |
| After one failed question, every next one fails too | `del messages[checkpoint:]` is missing, so a request without a result stays in the history | Add it, and make sure `checkpoint` is set before the user message is appended |
| A tool bug shows as "failed: KeyError" and not as the real error | `except (...)` catches `KeyError` and `TypeError` from **inside** a tool too, not only a bad call | Expected for a teaching app. In a real one, catch only around the lookup and the call, and log other errors |
| The model keeps retrying after an error | It has no way to succeed, as with the broken registry, and each retry spends a round | That is what `MAX_STEPS` is for. Keep it small |

Next: **Step 9 — Recap and Exercises**.
