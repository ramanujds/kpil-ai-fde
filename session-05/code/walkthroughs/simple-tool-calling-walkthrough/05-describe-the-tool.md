# Step 5 — Describe the Tool

> Back to index · Previous: Write the Tool · Next: Let the Model Decide

## Goal

Write the description of the tool: the information the model reads in order to decide
whether to use it, and what to fill in.

## Why this matters

The model never sees your function. It only sees this description. Everything it knows
about the tool, it learns here. A vague description gives the model nothing to decide with,
so it will pick the wrong tool, or ignore the right one.

The description answers three questions:

| Question | Answered by |
|---|---|
| What is the tool called? | `name` |
| What does it do, and when should I use it? | `description` |
| What does it need from me? | `parameters` |

The format is fixed by the API. You are not expected to invent it. Copy the shape and change
the words.

## 1. The Inputs

Add this below the function:

```python
# 2. The tool description: the menu the model reads. It never sees the function above.
#    It answers three questions: what is the tool called, what does it do, what does it need?

# What it needs: one input called order_id, which is text.
inputs = {
    "type": "object",
    "properties": {
        "order_id": {"type": "string", "description": "The order number, for example 4821"},
    },
    "required": ["order_id"],
}
```

This says: the tool takes one input called `order_id`, it is text, and it is required. The
`description` inside the input shows an example, which helps the model fill it in correctly.
`"object"` and `"properties"` are the standard wrapper. Copy them as they are.

## 2. The Description

```python
# What it is called and what it does. Say when to use it and when not to.
description = "Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."
```

Two things to notice. It says when to use the tool ("when the customer asks where their
order is") and when not to ("Do not use for refunds"). The second half is what stops the
model reaching for the wrong tool.

## 3. The Tool List

```python
# The tool list is a list because a model can be given many tools. Here there is only one.
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",  # same name as the Python function above
            "description": description,
            "parameters": inputs,
        },
    },
]
```

The list has one item because we have one tool. A model can be given many. The `name` must
match the Python function exactly, because Step 7 uses it to find the function to run.
`"type": "function"` is the label the API uses for this kind of tool.

## Try it

Add a temporary line at the bottom of the file, run, then remove it:

```python
print(tools)
```

```bash
uv run tool_calling.py
```

```text
...
[{'type': 'function', 'function': {'name': 'get_order_status', 'description': 'Look up the delivery status of an order. ...
```

Nothing else changes, because the model has not been given the list yet. That is Step 6.
**Delete the `print(tools)` line** before moving on.

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


# 2. The tool description: the menu the model reads. It never sees the function above.
#    It answers three questions: what is the tool called, what does it do, what does it need?

# What it needs: one input called order_id, which is text.
inputs = {
    "type": "object",
    "properties": {
        "order_id": {"type": "string", "description": "The order number, for example 4821"},
    },
    "required": ["order_id"],
}

# What it is called and what it does. Say when to use it and when not to.
description = "Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."

# The tool list is a list because a model can be given many tools. Here there is only one.
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",  # same name as the Python function above
            "description": description,
            "parameters": inputs,
        },
    },
]

messages = [{"role": "user", "content": "Where is my order 4821?"}]
print("User:", messages[0]["content"], "\n")

response = client.chat.completions.create(model=MODEL, messages=messages)
reply = response.choices[0].message

print("AI:", reply.content)
```

</details>

This is an intermediate version. It does not include the temporary `print(tools)`.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `SyntaxError` near `tools` | A missing comma or bracket in the nested dicts | Compare bracket by bracket with the checkpoint |
| The model later picks the wrong tool | The description is vague, such as "Gets stuff" | Say what it does, when to use it and when not to |
| `KeyError` or "unexpected argument" in Step 7 | The input in `inputs` has a different name from the function's parameter | Keep `order_id` identical in both places |
| The model later ignores the tool | `name` does not match the function, or the description does not match how users ask | Match the name and use the customer's own words in the description |

Next: **Step 6 — Let the Model Decide**.
