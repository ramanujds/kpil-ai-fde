# Step 6 — Let the Model Decide

> Back to index · Previous: Describe the Tool · Next: Run the Tool and Return the Result

## Goal

Send the tool list with the question, and look at what the model sends back when it wants a
tool. Do not run the tool yet.

## Why this matters

When a model decides to use a tool, it does not reply with text. It replies with a
structured request: a tool name and the values to use. If you have never looked at that raw
reply, tool calling feels like magic. Looking at it first shows exactly what the model is
doing, and it is where most bugs become visible. When a tool misbehaves later, this is the
first thing to read.

It also shows that the decision is the model's. For some questions it will ask for the
tool, and for others it will answer directly, so your code must handle both.

## 1. Pass the Tool List

Replace the plain call with one that includes `tools`:

```python
# 3. First call: send the question together with the tool list.
response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
reply = response.choices[0].message
```

The only change is `tools=tools`. The reply may now be text, or a request for a tool.

## 2. Read the Tool Request

Add `import json` at the top of the file, above the other imports:

```python
import json

from dotenv import load_dotenv
from openai import OpenAI
```

Then add below the call:

```python
if reply.tool_calls:
    # The model did not answer. It asked us to run a tool.
    for call in reply.tool_calls:
        arguments = json.loads(call.function.arguments)
        print(f"Model asks for: {call.function.name}({arguments})")
```

`reply.tool_calls` is empty when the model answered directly, so the `if` only runs when the
model asked for a tool. Each request has a function name and `arguments`, which arrive as
JSON **text**, not as a dict. `json.loads` turns the text into a dict, such as
`{'order_id': '4821'}`.

Keep the final `print` at the bottom:

```python
print("AI:", reply.content)
```

## Try it

```bash
uv run tool_calling.py
```

```text
User: Where is my order 4821?

Model asks for: get_order_status({'order_id': '4821'})
AI: None
```

Two things to notice. The model asked for the tool and filled in `order_id` by itself, from
your question. And `AI: None`, because a tool request has no text. There is nothing to
print yet, and no answer.

Now change the question in `messages` to `"Hi, how are you?"` and run again:

```text
User: Hi, how are you?

AI: Hello! I'm doing well, thank you. How can I assist you today?
```

No tool request, so the `if` was skipped and the answer is plain text. Change the question
back to `"Where is my order 4821?"` before moving on.

## Checkpoint

<details>
<summary>Full <code>tool_calling.py</code> after this step</summary>

```python
import json

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

# 3. First call: send the question together with the tool list.
response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
reply = response.choices[0].message

if reply.tool_calls:
    # The model did not answer. It asked us to run a tool.
    for call in reply.tool_calls:
        arguments = json.loads(call.function.arguments)
        print(f"Model asks for: {call.function.name}({arguments})")

print("AI:", reply.content)
```

</details>

This is an intermediate version. Step 7 completes it.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `AI: None` for the order question | Expected at this step: a tool request has no text | Continue to Step 7, which sends the result back |
| The model answers the order question directly | The description does not match the question, or `tools=tools` is missing from the call | Check the call and the description |
| `NameError: json` | `import json` is missing | Add it at the top |
| `TypeError` on `arguments` | Used `call.function.arguments` as a dict | It is text; wrap it in `json.loads(...)` |

Next: **Step 7 — Run the Tool and Return the Result**.
