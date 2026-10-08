# Step 6 — Look Up the Tool by Name

> Back to index · Previous: Run the Tool and Return the Result · Next: Handle an Unknown Tool

## Goal

Stop naming `get_order_status` inside the loop. Build a dictionary from tool name to tool, and
use the name in the model's request to pick the function to run.

## Why this matters

Look at this line from Step 5:

```python
result = get_order_status.invoke(call["args"])
```

It runs `get_order_status` **whatever the model asked for**. The request names a tool in
`call["name"]`, and the line ignores it. With one tool this is harmless, because the only
possible name is `get_order_status`. Give the model a second tool and the program breaks
quietly: the model asks for `cancel_order`, and your code runs `get_order_status` with the
cancel arguments. Nothing crashes, and the wrong thing happens.

The fix is an old trick: a menu card. Keep a dictionary from name to tool, and when the
model's request arrives, look the name up. The name the model sends is just text, and a
dictionary is the natural way to turn text into the thing it refers to. The other option is a
growing `if name == ...` / `elif name == ...` chain, which needs a new branch for every tool
you add.

The dictionary is built from the same list you give to `bind_tools`. That list is the single
place that says which tools exist. Add a tool to it and both the model and the lookup know.

## 1. Make the Tool List a Variable

In the "Give the tools to the model" section, put the list in a variable so it can be used
twice:

```python
# 2. Give the tools to the model.
# CHANGED: bind_tools() replaces passing tools=tools on every call.
tools = [get_order_status]
model_with_tools = model.bind_tools(tools)
```

## 2. Build the Lookup

Directly under it, add:

```python
# Name -> tool lookup. The model answers with a tool name as text, so we use this
# dictionary to find the matching function instead of hardcoding one tool in the loop.
# Add a tool to the list above and it is picked up here automatically.
tools_by_name = {t.name: t for t in tools}
```

`t.name` is the same name you printed in Step 3: the function's name. For this list the
result is `{"get_order_status": <the tool>}`.

## 3. Use It in the Loop

Replace the line that runs the function:

```python
        # 4. Our code runs the real function, chosen by the name the model sent.
        # CHANGED: a tool made with @tool is run with .invoke(), passing the arguments dict.
        selected_tool = tools_by_name[call["name"]]
        result = selected_tool.invoke(call["args"])
```

Two lines instead of one, with a named step in between. `selected_tool` is whichever tool the
model asked for.

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

The output is the same as Step 5. With one tool there is nothing to see, which is the point:
the behaviour did not change, but the loop no longer depends on there being only one tool.
To see the benefit, do the experiment in the first exercise in Step 11 later: add a second
tool to the `tools` list and change nothing else.

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
tools = [get_order_status]
model_with_tools = model.bind_tools(tools)

# Name -> tool lookup. The model answers with a tool name as text, so we use this
# dictionary to find the matching function instead of hardcoding one tool in the loop.
# Add a tool to the list above and it is picked up here automatically.
tools_by_name = {t.name: t for t in tools}

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

        # 4. Our code runs the real function, chosen by the name the model sent.
        # CHANGED: a tool made with @tool is run with .invoke(), passing the arguments dict.
        selected_tool = tools_by_name[call["name"]]
        result = selected_tool.invoke(call["args"])
        print("Tool returned:", result, "\n")

        # 5. Send the result back, tagged with the id of the request it answers.
        # CHANGED: ToolMessage replaces {"role": "tool", "tool_call_id": ..., "content": ...}.
        messages.append(ToolMessage(result, tool_call_id=call["id"]))

    # 6. Second call: the model reads the result and writes the final answer.
    reply = model_with_tools.invoke(messages)

print("AI:", reply.content)
```

</details>

This is an intermediate version and does not match the reference yet. Two small changes
remain, both in Step 7.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `NameError: tools` | The list was left inline in `bind_tools([...])` | Define `tools = [...]` first, then `bind_tools(tools)` |
| `KeyError: 'some_name'` | The model asked for a name that is not in the dictionary | Step 7 handles this case |
| The dictionary is empty | `tools_by_name` was built before `tools` was defined | Put it after the `tools = [...]` line |
| A tool is in the dictionary but the model never uses it | It was added to `tools_by_name` by hand but not to the list passed to `bind_tools` | Add it to `tools` only. Both the model and the lookup read from that list |

Next: **Step 7 — Handle an Unknown Tool**.
