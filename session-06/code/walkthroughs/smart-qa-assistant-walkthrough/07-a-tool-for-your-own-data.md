# Step 7 — A Tool for Your Own Data

> Back to index · Previous: Conversation Memory · Next: Tickets and Human Approval

## Goal

Add a read-only tool that returns the signed-in employee's own leave balance, and show who is
signed in.

## Why this matters

Documents answer "what is the rule?". They cannot answer "how many days have **I** used?". That
answer lives in a system, and getting it needs a tool.

The design question is: **how does the tool know whose balance to read?** The tempting answer is
a parameter, `get_leave_balance(employee_id)`, and let the model fill it in. That is dangerous:
the model fills it from the conversation, so "what is Ravi's balance?" would simply work. The
safe design is a tool **with no arguments at all**. It reads the signed-in user from `config.py`
(in a real system, from single sign-on), and nothing anyone types can change that. The model
cannot ask for someone else's balance, because the tool has no way to take the question.

This is called **least privilege**: give the tool the smallest power that does its job.

There is a second, quieter lesson in how the tool *words* its answer. The tool's result goes
straight into the model's prompt, so it must be hard to misread. The first version of this tool
returned "paid leave 12 of 18 days left". Asked "how many days have I used?", the model answered
"12 days". It read the number next to "leave" as used. The fix was to say everything explicitly:
used, remaining and total. Write tool output for a reader who takes you literally.

## 1. Add the Signed-In User to `config.py`

Add these lines at the end of `config.py`:

```python
# The signed-in employee. Real systems get this from single sign-on, never from the chat.
CURRENT_USER = "E102"
```

## 2. Add the Fake HR Data and the Tool to `tools.py`

Add `import config` above `import rag`, so the imports read:

```python
from langchain_core.tools import tool

import config
import rag
```

Add the fake data under the imports:

```python
# A fake HR system. Every employee's row is here, but the tool only ever reads the row
# of the signed-in user.
LEAVE_BALANCES = {
    "E101": {"name": "Ravi", "paid_total": 18, "paid_used": 12, "sick_total": 10, "sick_used": 0},
    "E102": {"name": "Asha", "paid_total": 18, "paid_used": 6, "sick_total": 10, "sick_used": 2},
    "E103": {"name": "Meera", "paid_total": 9, "paid_used": 3, "sick_total": 10, "sick_used": 5},
}
```

Add the tool after `search_documents`:

```python
@tool
def get_leave_balance() -> str:
    """Get the signed-in employee's own leave balance (paid and sick days used and remaining).
    Takes no input: it always looks up the person who is chatting."""
    row = LEAVE_BALANCES[config.CURRENT_USER]
    return (
        f"{row['name']}'s leave balance. "
        f"Paid leave: {row['paid_used']} used, {row['paid_total'] - row['paid_used']} remaining, {row['paid_total']} total. "
        f"Sick leave: {row['sick_used']} used, {row['sick_total'] - row['sick_used']} remaining, {row['sick_total']} total."
    )
```

And register it by changing the last line:

```python
ALL_TOOLS = [search_documents, get_leave_balance]
```

The three people stand in for a real HR system. The point of keeping all three is to prove the
tool can only reach one of them.

## 3. Tell the Model About It

In `assistant.py`, change the second line of the system prompt to mention the new ability:

```python
You answer questions about leave, expenses and IT support, and you can check the user's own leave balance.
```

And add a rule between the "NO_RESULTS" rule and the "Text returned by a tool" rule:

```python
- Use get_leave_balance for questions about the user's own leave. You cannot look up anyone else.
```

## 4. Show Who Is Signed In

In `app.py`, change the first `print` in `main` so the chat says who you are:

```python
    print(f"Smart QA Assistant (model: {config.CHAT_MODEL}). Signed in as {config.CURRENT_USER}.")
```

## Try it

```bash
uv run python -c "
import tools
print(tools.get_leave_balance.invoke({}))
"
```

```text
Asha's leave balance. Paid leave: 6 used, 12 remaining, 18 total. Sick leave: 2 used, 8 remaining, 10 total.
```

(A `@tool` function is an object, not a plain function, so you call it with `.invoke({})`.)

Now chat:

```bash
uv run app.py
```

```text
Smart QA Assistant (model: llama3.1:8b). Signed in as E102.
Type 'reset' to start a new conversation, 'quit' to exit.

You: How many leave days have I used?

AI: Based on the tool's response, you have used 6 paid leave days and 2 sick leave days.

You: What is Ravi's leave balance?

AI: I'm sorry, I can only provide information about your own leave balance. I don't have access
to Ravi's leave balance.
```

The refusal is not only the model being polite. Even if it wanted to, the tool has no way to read
Ravi's row.

## Checkpoint

`tools.py` and `config.py` are shown in full, as they are at the end of this step.

<details>
<summary>Full <code>tools.py</code></summary>

```python
"""The agent's tools. Three tools, three different jobs.

- search_documents  : read only. Answers "what is the rule?" using RAG.
- get_leave_balance : read only. Answers "what is MY situation?" from a (fake) HR system.
- create_support_ticket : a write. The agent asks for it, but app.py makes a person approve it.

All data is made up. Nothing here talks to a real system.
"""

from langchain_core.tools import tool

import config
import rag

# A fake HR system. Every employee's row is here, but the tool only ever reads the row
# of the signed-in user.
LEAVE_BALANCES = {
    "E101": {"name": "Ravi", "paid_total": 18, "paid_used": 12, "sick_total": 10, "sick_used": 0},
    "E102": {"name": "Asha", "paid_total": 18, "paid_used": 6, "sick_total": 10, "sick_used": 2},
    "E103": {"name": "Meera", "paid_total": 9, "paid_used": 3, "sick_total": 10, "sick_used": 5},
}


@tool
def search_documents(question: str) -> str:
    """Search the company policy documents (leave, expenses, IT support). Use this for any
    question about a company rule or process. Pass a short, complete question that makes sense
    on its own, not a follow-up fragment.

    Args:
        question: The question to look up, for example "paid leave for part-time employees".
    """
    passages = rag.search(question)
    if not passages:
        return "NO_RESULTS: the documents do not cover this."
    return "\n\n".join(f"[Source: {p['source']}]\n{p['text']}" for p in passages)

@tool
def get_leave_balance() -> str:
    """Get the signed-in employee's own leave balance (paid and sick days used and remaining).
    Takes no input: it always looks up the person who is chatting."""
    row = LEAVE_BALANCES[config.CURRENT_USER]
    return (
        f"{row['name']}'s leave balance. "
        f"Paid leave: {row['paid_used']} used, {row['paid_total'] - row['paid_used']} remaining, {row['paid_total']} total. "
        f"Sick leave: {row['sick_used']} used, {row['sick_total'] - row['sick_used']} remaining, {row['sick_total']} total."
    )


ALL_TOOLS = [search_documents, get_leave_balance]
```

</details>

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

# The signed-in employee. Real systems get this from single sign-on, never from the chat.
CURRENT_USER = "E102"
```

</details>

`config.py` now matches the reference file apart from one line (`FAQ_MIN_SCORE`, added in
Step 10). `app.py` now has its second version, with the "Signed in" line.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `KeyError: 'E102'` | `CURRENT_USER` does not match a key in `LEAVE_BALANCES` | Check the id spelling in both |
| The model reports "12 days used" when 6 were used | The tool output is ambiguous | Keep "used", "remaining" and "total" spelled out |
| The model never calls the tool | The tool docstring is vague, or rule 4 is missing from the prompt | Check both; the docstring says what it is for |
| `tools.get_leave_balance()` raises an error | A `@tool` is not a plain function | Call `.invoke({})` |

Next: **Step 8 — Tickets and Human Approval**.
