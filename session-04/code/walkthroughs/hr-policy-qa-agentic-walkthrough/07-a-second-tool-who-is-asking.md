# Step 7 — A Second Tool, Who Is Asking

> Back to index · Previous: The Agent Loop · Next: Handle Failures

## Goal

Add a tool that returns the signed-in employee's own record, so the assistant can answer
questions whose answer depends on who is asking, and make sure it can never read anyone
else's record.

## Why this matters

Until now, the only tool was search, and the loop rarely did more than one round. A second
tool changes that, because now the model has to **choose between tools**, and sometimes use
them one after the other.

Take "What is my notice period?". The policy says 30 days on probation, 60 for confirmed
employees and 90 for managers. The right answer is a fact about the **person** joined to a
rule about the **policy**. The model cannot search for the person, and the policy search
cannot know the person. So it needs two rounds: get the profile first, then search for the
rule that fits it. This is exactly what the one-round code in Step 5 could not do.

Notice what is **not** in the code: any rule about probation or notice periods. The code
only fetches a record. The policy text, retrieved by search, says what the record means.
When the policy changes, you change the document and run `ingest.py`, and `ask.py` stays
the same.

There is a safety point in the design. The tool takes **no arguments**. It cannot be asked
for "E103's record" or "everyone in Finance", because the model has no way to name another
person. It can only get the record of whoever signed in. That is access control done by
shape: a tool that cannot ask the question cannot leak the answer. A tool that took an
employee ID would need its own check, and a model can be talked into passing someone else's
ID. Every tool is a door, so for every door ask who may go through it.

## 1. Add the Imports

Change the first lines to bring in dates and file paths:

```python
import json
from datetime import date
from pathlib import Path

import chromadb
```

## 2. Load the Employees

Directly below the line that opens the collection, add:

```python
employees = json.loads(Path("employees.json").read_text())
```

This reads the file you created in Step 2.

## 3. Write the Tool

Below `search_policies`, add:

```python


def get_my_profile():
    # Only the signed-in user's own record is ever returned. The model cannot ask for anyone else's.
    joined = date.fromisoformat(me["joined"])
    today = date.today()
    months = (today.year - joined.year) * 12 + today.month - joined.month - (today.day < joined.day)
    return json.dumps({**me, "months_of_service": months, "today": today.isoformat()})
```

| Part | What it does |
|---|---|
| `me` | The record of the signed-in employee. It is set in part 6, when the program starts. The function reads it when called |
| `months` | Whole months since joining: the difference in months, minus one if the day of the month has not been reached yet |
| `{**me, ...}` | The person's record plus the two worked-out values |
| `"months_of_service"` | The model would otherwise have to do date arithmetic, which models are poor at. The code does it, so the model only reads the number |
| `"today"` | Lets the model say "as of" a date, and see that the figure is current |

## 4. Register and Describe It

Change the registry to include both tools:

```python
TOOL_FUNCTIONS = {"search_policies": search_policies, "get_my_profile": get_my_profile}
```

At the end of the `TOOLS` list, after the closing of the search entry, add a second entry:

```python
    {
        "type": "function",
        "function": {
            "name": "get_my_profile",
            "description": "Get the signed-in employee's name, role, level, department, joining date and months of service.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
```

`"properties": {}` is how you say that a tool takes no arguments.

## 5. Teach the Model When to Use It

Replace `SYSTEM` with the full version below. The first line changes, and the profile rule
is new:

```python
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
```

The rule says **first**, and **then search for the rule**. Without it, the model tends to
answer "if you are on probation, it is 30 days", which hands the user the work of finding
out. "Never ask the user for facts the profile has" closes that gap.

## 6. Sign In

Below `run_agent` and above the welcome line, add the sign-in, and change the welcome
message to use the name:

```python
employee_id = input("Your employee ID (for example E101): ").strip().upper()
if employee_id not in employees:
    raise SystemExit(f"Unknown employee ID. Try one of: {', '.join(employees)}")
me = employees[employee_id]

print(f"\nHello {me['name']}. Ask about company policies. Type 'quit' to exit.\n")
```

There is no password because the data is made up, and this is a teaching app. A real system
would take the identity from the company's sign-in, never from something the user types.
The point of this step is the shape of the tool, not the login.

## Try it

```bash
uv run ask.py
```

Sign in as E101, the newest joiner:

```text
Your employee ID (for example E101): E101

Hello Priya Nair. Ask about company policies. Type 'quit' to exit.

You: What is my notice period?
  -> get_my_profile()
  -> search_policies(query='notice period', document='HR Handbook')
AI: Your notice period is 30 days since you are currently on probation, as you have been with
the company for less than 6 months. ... [HR Handbook > Notice Period].
Retrieved from:
  - HR Handbook > Notice Period
  - HR Handbook > Probation
  - HR Handbook > Grievance Redressal

You: Can I work from home?
  -> search_policies(query='work from home', document='Work From Home Policy')
AI: As you are currently on probation, you are required to work from the office full time
unless your manager approves a one-off request. ... [Work From Home Policy > Eligibility].
```

Two rounds for the first question, in the right order: who, then what rule. The second
question reused what the first had already revealed, so the profile was not fetched again.
It is still in the history.

Quit and run it again as E103, a manager:

```text
Your employee ID (for example E101): E103

Hello Meera Iyer. Ask about company policies. Type 'quit' to exit.

You: What is my notice period?
  -> get_my_profile()
  -> search_policies(query='notice period', document='HR Handbook')
AI: Your notice period is 90 days, as you are a Manager. ... [HR Handbook > Notice Period].
```

The same question gives 30 days for one person and 90 for the other. The documents did not
change, and the code did not change. Only the profile did.

A question that does not depend on the user should leave the profile unused. Sign in as
E102 and ask "Can I carry forward unused leave?":

```text
You: Can I carry forward unused leave?
  -> search_policies(query='carry forward unused leave', document='Leave Policy')
AI: You can carry forward unused paid leave of up to 6 days ... this does not apply to
employees in their first year of service ... [Leave Policy > Carry Forward of Leave].
```

This answer is a general one, with the first-year exception stated. It could also have
looked the profile up and told Rahul he is past his first year. The model chose not to, and
a different run might choose differently. That is the nature of an agent, and Step 9
returns to it.

## Checkpoint

<details>
<summary>Full <code>ask.py</code> after this step</summary>

```python
import json
from datetime import date
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

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
    name = call.function.name
    args = json.loads(call.function.arguments or "{}")
    shown = ", ".join(f"{key}={value!r}" for key, value in args.items())
    print(f"  -> {name}({shown})")
    return TOOL_FUNCTIONS[name](**args)


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

    retrieved.clear()
    messages.append({"role": "user", "content": question})

    answer = run_agent(messages)

    print("AI:", answer)
    if retrieved:
        print("Retrieved from:")
        for source in dict.fromkeys(retrieved):  # unique, in the order they were read
            print(f"  - {source}")
    print()
```

</details>

This file is not finished. Step 8 adds error handling and holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: employees.json` | The file is missing, or you ran from another folder | Create it as in Step 2, and run `uv run ask.py` from `hr-policy-qa-agentic` |
| `NameError: name 'me' is not defined` | The sign-in block was placed after the loop, or never added | Put the sign-in directly above the welcome line, before the question loop |
| The model answers "if you are on probation..." and never calls the profile tool | The model skipped the tool. This happens, and it is more likely with a small model | Check that the profile rule is in `SYSTEM`. Then ask again. See Exercise 4 |
| The answer says the wrong probation status after some months | `joined` in `employees.json` is a fixed date, and the months move on | Change the dates in `employees.json` |
| `Unknown employee ID` | A lower-case or mistyped ID | IDs are `E101` to `E104`. The code upper-cases what you type |

Next: **Step 8 — Handle Failures**.
