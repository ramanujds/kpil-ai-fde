# Step 4 — Write the Tool

> Back to index · Previous: Your First Call · Next: Describe the Tool

## Goal

Write the tool itself: an ordinary Python function that looks up an order. No model is
involved yet.

## Why this matters

A tool is only a function. Writing and testing it on its own, before any model is involved,
separates two kinds of bug: "the tool is broken" and "the model chose badly". When something
goes wrong later you will know which one to look at.

The function also shows two habits of a good tool. It does one small job. And when it finds
nothing, it returns a readable sentence instead of crashing, so the model can pass the
message on or ask the user to check the number.

## 1. The Function

Add this between `MODEL` and `messages`:

```python
# 1. The tool: a plain Python function. The model never runs this, our code does.
def get_order_status(order_id: str) -> str:
    orders = {
        "4821": "Shipped, arrives Thursday",
        "4822": "Packed, ships tomorrow",
    }
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")
```

| Line | What it does |
|---|---|
| `orders = {...}` | A tiny fake order table, so there is nothing to connect to |
| `orders.get(order_id, ...)` | Looks up the order, or uses the second value if it is missing |
| The fallback sentence | Tells the reader what went wrong and what to try next |

Order numbers are text (`"4821"`, not `4821`). That choice matters in Step 5, where the
description says the input is text.

## Try it

Add a temporary test at the very bottom of the file:

```python
print(get_order_status("4821"))
print(get_order_status("9999"))
```

```bash
uv run tool_calling.py
```

```text
User: Where is my order 4821?

AI: ...
Shipped, arrives Thursday
No order found with number 9999. Check the number and try again.
```

The lines from Step 3 still run first. Look at the last two lines, which come from your
function. When you are satisfied, **delete the two test lines**.

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


# 1. The tool: a plain Python function. The model never runs this, our code does.
def get_order_status(order_id: str) -> str:
    orders = {
        "4821": "Shipped, arrives Thursday",
        "4822": "Packed, ships tomorrow",
    }
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


messages = [{"role": "user", "content": "Where is my order 4821?"}]
print("User:", messages[0]["content"], "\n")

response = client.chat.completions.create(model=MODEL, messages=messages)
reply = response.choices[0].message

print("AI:", reply.content)
```

</details>

This is an intermediate version. It does not include the temporary test lines.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `get_order_status(4821)` says not found | The key in the table is the string `"4821"`, and you passed a number | Pass `"4821"` with quotes |
| `NameError: get_order_status` | The function is defined below the line that uses it | Put the function above the test lines |
| The test lines stay in the file | Forgot to delete them | Remove them before Step 5 so the output stays clean |

Next: **Step 5 — Describe the Tool**.
