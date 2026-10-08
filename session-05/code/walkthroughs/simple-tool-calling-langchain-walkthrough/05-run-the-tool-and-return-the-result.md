# Step 5 — Run the Tool and Return the Result

> Back to index · Previous: Give the Tool to the Model · Next: Look Up the Tool by Name

## Goal

Run the tool with the arguments the model chose, send the result back, and print the model's
final answer. This completes the round trip, with the tool still named by hand.

## Why this matters

The model asked for a tool, but nothing has happened yet. Your code must run it and tell the
model what came back. The model has no memory between calls, so the second call must carry
the whole story: the question, the model's own request, and the result. Miss one piece and
the API rejects the call.

LangChain trims three details compared with the plain SDK:

| Plain SDK | LangChain |
|---|---|
| `json.loads(call.function.arguments)` | `call["args"]` is already a dictionary |
| `get_order_status(**arguments)` | `get_order_status.invoke(call["args"])` |
| `{"role": "tool", "tool_call_id": ..., "content": ...}` | `ToolMessage(result, tool_call_id=call["id"])` |

Each `call` is now a dictionary with `name`, `args` and `id`, not an object with nested
attributes. That is the only reason the loop reads differently.

This step still writes `get_order_status` into the loop by name. It works, but notice that
line. Step 6 is about it.

## 1. Add `ToolMessage`

Extend the messages import:

```python
from langchain_core.messages import HumanMessage, ToolMessage
```

## 2. Replace the Two Temporary Prints

Delete the two `print` lines from Step 4 and write the round trip in their place:

```python
# CHANGED: tool_calls is already a list of dicts. No json.loads needed.
if reply.tool_calls:
    # The model did not answer. It asked us to run one or more tools.
    messages.append(reply)

    for call in reply.tool_calls:
        print(f"Model asks for: {call['name']}({call['args']})")

        # 4. Our code runs the real function.
        # CHANGED: a tool made with @tool is run with .invoke(), passing the arguments dict.
        result = get_order_status.invoke(call["args"])
        print("Tool returned:", result, "\n")

        # 5. Send the result back, tagged with the id of the request it answers.
        # CHANGED: ToolMessage replaces {"role": "tool", "tool_call_id": ..., "content": ...}.
        messages.append(ToolMessage(result, tool_call_id=call["id"]))

    # 6. Second call: the model reads the result and writes the final answer.
    reply = model_with_tools.invoke(messages)

print("AI:", reply.content)
```

| Line | What it does |
|---|---|
| `if reply.tool_calls` | An empty list means the model answered directly, so skip to the print |
| `messages.append(reply)` | The model's request goes into the conversation before its result |
| `for call in reply.tool_calls` | The model can ask for more than one tool in a single reply |
| `get_order_status.invoke(call["args"])` | Your code runs the function. The model only asked |
| `ToolMessage(result, tool_call_id=call["id"])` | Tags the result with the id of the request it answers |
| `model_with_tools.invoke(messages)` | The second call, now with three messages in the list |

By this point `messages` holds three items: the `HumanMessage`, the model's reply (with its
tool request and no text), and the `ToolMessage`.

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

The final sentence will be worded differently on each run. Now try these questions:

| Change the question to | What you should see |
|---|---|
| `"Hi, how are you?"` | No tool request, one model call, a plain greeting |
| `"Where is my order 9999?"` | The tool returns the "not found" sentence, and the model passes it on |
| `"I want a refund for order 4821"` | Often no tool call, because of "Do not use for refunds" in the docstring |

## Checkpoint

<details>
<summary>Full <code>tool_calling.py</code> after this step</summary>

```python
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# Reads OPENAI_API_KEY from the .env file. ChatOpenAI picks it up automatically.
load_dotenv()

# CHANGED: one LangChain model object replaces the OpenAI client.
model = ChatOpenAI(model="gpt-4o-mini")

# A fake order table shared by all the tools.
orders = {
    "4821": "Shipped, arrives Thursday",
    "4822": "Packed, ships tomorrow",
}


# 1. The tools: plain Python functions. The model never runs these, our code does.
# CHANGED: the @tool line replaces the whole hand-written tool description.
# LangChain builds it from the function name, the type hints (order_id: str) and the
# docstring below. The docstring is what the model reads, so say when to use it.
@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."""
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


# 2. Give the tools to the model.
# CHANGED: bind_tools() replaces passing tools=tools on every call.
model_with_tools = model.bind_tools([get_order_status])

messages = [HumanMessage("Where is my order 4821?")]
print("User:", messages[0].content, "\n")

# 3. First call: the model sees the question and the tools.
# CHANGED: invoke() replaces client.chat.completions.create(...).
reply = model_with_tools.invoke(messages)

# CHANGED: tool_calls is already a list of dicts. No json.loads needed.
if reply.tool_calls:
    # The model did not answer. It asked us to run one or more tools.
    messages.append(reply)

    for call in reply.tool_calls:
        print(f"Model asks for: {call['name']}({call['args']})")

        # 4. Our code runs the real function.
        # CHANGED: a tool made with @tool is run with .invoke(), passing the arguments dict.
        result = get_order_status.invoke(call["args"])
        print("Tool returned:", result, "\n")

        # 5. Send the result back, tagged with the id of the request it answers.
        # CHANGED: ToolMessage replaces {"role": "tool", "tool_call_id": ..., "content": ...}.
        messages.append(ToolMessage(result, tool_call_id=call["id"]))

    # 6. Second call: the model reads the result and writes the final answer.
    reply = model_with_tools.invoke(messages)

print("AI:", reply.content)
```

</details>

This is an intermediate version and does not match the reference yet. It is the complete
simple-tool-calling-langchain app as it stood before the tool lookup was added.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| A 400 error saying a `tool` message must follow a message with `tool_calls` | Forgot `messages.append(reply)` before the result | Append the model's reply first |
| A 400 error about a missing or wrong `tool_call_id` | The `ToolMessage` has no id, or the wrong one | Use `call["id"]` from the request |
| `AI:` prints empty text | The second call was skipped, or indented inside the `for` loop | Keep it inside the `if` but outside the `for` loop |
| A validation error from `.invoke` | You passed `call` instead of `call["args"]` | Pass only the arguments dictionary |
| `NameError: ToolMessage` | The import line was not extended | Add `ToolMessage` to the `langchain_core.messages` import |

Next: **Step 6 — Look Up the Tool by Name**.
