# Step 7 — Run the Tool and Return the Result

> Back to index · Previous: Let the Model Decide · Next: Recap and Exercises

## Goal

Run the real function with the values the model chose, send the result back, and print the
model's final answer. This completes the round trip.

## Why this matters

The model asked for a tool, but nothing has happened yet. Your code must run the function
and tell the model what came back. Only then can the model write an answer from real data
instead of guessing.

The model has no memory between calls. For the second call it can only use what you send,
so you must send the whole story: the question, the model's own request, and the result. If
any one piece is missing, the model cannot connect the result to the question and the API
rejects the request.

## 1. Remember the Model's Request

Inside the `if`, first add the model's reply to the conversation:

```python
if reply.tool_calls:
    # The model did not answer. It asked us to run a tool.
    messages.append(reply)
```

The result you send in a moment must follow the message that asked for it, so that message
has to be in the list.

## 2. Run the Function

Inside the `for` loop, after the print, run the real function:

```python
        # 4. Our code runs the real function.
        result = get_order_status(**arguments)
        print("Tool returned:", result, "\n")
```

`**arguments` turns the dict `{'order_id': '4821'}` into `order_id='4821'`, which is how the
function expects it. This is the moment your code, not the model, does the work. Here is
also where you would check the request, limit it or ask for approval. Block 3 of Day 5 adds
exactly that.

## 3. Send the Result Back

```python
        # 5. Send the result back, tagged with the id of the request it answers.
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
```

The result goes into a message with `role` set to `"tool"`. `tool_call_id` says which request
it answers, so the model can match them when it has asked for several.

## 4. Ask Again

After the loop, outside it, call the model a second time:

```python
    # 6. Second call: the model reads the result and writes the final answer.
    response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    reply = response.choices[0].message
```

The second call has the tool list too, in case the model needs another tool. Because it now
has the result, it writes the answer in text. The final `print("AI:", reply.content)` then
shows it.

By this point `messages` holds three items:

| # | Role | Content |
|---|---|---|
| 1 | `user` | Where is my order 4821? |
| 2 | `assistant` | A request for `get_order_status` with `order_id` 4821 (no text) |
| 3 | `tool` | Shipped, arrives Thursday |

## Try it

```bash
uv run tool_calling.py
```

```text
User: Where is my order 4821?

Model asks for: get_order_status({'order_id': '4821'})
Tool returned: Shipped, arrives Thursday

AI: Your order 4821 has shipped and will arrive on Thursday.
```

The final sentence will be worded differently on each run. Now try these:

| Change the question to | What you should see |
|---|---|
| `"Hi, how are you?"` | No tool request, one model call, a plain greeting |
| `"Where is my order 9999?"` | The tool returns the "not found" sentence, and the model passes it on |
| `"I want a refund for order 4821"` | Often no tool call, because of "Do not use for refunds" in the description |

## Checkpoint

<details>
<summary>Full <code>tool_calling.py</code></summary>

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
    messages.append(reply)

    for call in reply.tool_calls:
        arguments = json.loads(call.function.arguments)
        print(f"Model asks for: {call.function.name}({arguments})")

        # 4. Our code runs the real function.
        result = get_order_status(**arguments)
        print("Tool returned:", result, "\n")

        # 5. Send the result back, tagged with the id of the request it answers.
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    # 6. Second call: the model reads the result and writes the final answer.
    response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    reply = response.choices[0].message

print("AI:", reply.content)
```

</details>

This matches `simple-tool-calling/tool_calling.py` in the reference project exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| A 400 error saying a `tool` message must follow a message with `tool_calls` | Forgot `messages.append(reply)` before sending the result | Append the model's reply first |
| A 400 error about a missing `tool_call_id` | The tool message has no `tool_call_id`, or it has the wrong one | Use `call.id` from the request |
| The model repeats itself or asks again | The tool message was not added, or was added to the wrong list | Print `messages` before the second call and check for three items |
| `TypeError: unexpected keyword argument` | The model sent an input name the function does not have | Make the input name in `inputs` and the function parameter identical |
| `AI: None` again | The second call was indented inside the `for` loop, or was skipped | Keep it inside the `if` but outside the `for` loop |

Next: **Step 8 — Recap and Exercises**.
