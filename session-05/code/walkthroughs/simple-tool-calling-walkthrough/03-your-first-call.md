# Step 3 — Your First Call

> Back to index · Previous: Project Setup · Next: Write the Tool

## Goal

Send one plain question about an order to the model and print the answer, with no tools yet.
This proves the connection works and shows what the model cannot do alone.

## Why this matters

If you build the connection, the tool and the round trip all at once and something breaks,
you cannot tell which part is at fault. A plain call first means every later problem
belongs to the new thing you just added.

It also sets up the motivation. Ask a model about order 4821 and it has nothing to go on. It
will apologise, or worse, invent a status. Step 7 fixes this.

## 1. Imports, Key and Client

Create `tool_calling.py`:

```python
from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"
```

`load_dotenv()` copies the lines of `.env` into the environment. `OpenAI()` then finds
`OPENAI_API_KEY` by itself, so the key never appears in the code.

## 2. The Question

Add below:

```python
messages = [{"role": "user", "content": "Where is my order 4821?"}]
print("User:", messages[0]["content"], "\n")
```

`messages` is a list. Each item is a dict with a `role` and the `content`. Here there is one
item, from the `user`. The `print` shows the question first so the output reads like a
conversation.

## 3. Send It and Print the Answer

```python
response = client.chat.completions.create(model=MODEL, messages=messages)
reply = response.choices[0].message

print("AI:", reply.content)
```

The response holds a list called `choices`. You asked for one answer, so you take the first
one and read its `message`. The message has a `content` field, which is the text.

## Try it

```bash
uv run tool_calling.py
```

```text
User: Where is my order 4821?

AI: I'm sorry, but I can't access order information. Please check the retailer's website or contact their customer support.
```

The exact wording will differ. The point is that the model cannot see your orders.

## Checkpoint

<details>
<summary>Full <code>tool_calling.py</code> after this step</summary>

```python
from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"

messages = [{"role": "user", "content": "Where is my order 4821?"}]
print("User:", messages[0]["content"], "\n")

response = client.chat.completions.create(model=MODEL, messages=messages)
reply = response.choices[0].message

print("AI:", reply.content)
```

</details>

This is an intermediate version. Step 7 turns it into the final `tool_calling.py`.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Missing credentials` or `api_key must be set` | `.env` is missing, empty or in another folder | Create `.env` next to `tool_calling.py` with the key |
| `Incorrect API key provided` | Typo, quotes or spaces in the key | Re-copy the key into `.env` |
| `ModuleNotFoundError: openai` | Ran with plain `python` | Use `uv run tool_calling.py` |
| `RateLimitError` or a quota message | Your key has no remaining quota, or you sent too many requests | Wait a minute, then check the key's limits with the trainer |

Next: **Step 4 — Write the Tool**.
