# Step 7 — Handle an Unknown Tool

> Back to index · Previous: Look Up the Tool by Name · Next: Keep a Conversation

## Goal

Make the loop survive a tool name that is not in the dictionary, and finish the single-question
version of the program.

## Why this matters

The tool name in the model's request is text that a model wrote. Most of the time it matches
a tool you gave it. Not always. Models sometimes shorten a name, change its case, or ask for
a tool that existed earlier in a conversation. With `tools_by_name[call["name"]]` any of
these raises a `KeyError` and the whole program stops.

The better behaviour is the one a good assistant would show. Tell the model "I do not have
that tool". The model can then try another way or explain to the customer what it cannot do.
So the guard does not raise an error. It sends back a sentence as the tool result, and the
loop carries on.

The same idea explains the other small change. A `ToolMessage` needs its content as text. A
tool might one day return a number, a list or `None`. `str(result)` turns whatever came back
into text, so the loop does not fail on a tool that returns something other than a string.

## 1. Use `.get` and a Guard

Replace the two lines that pick and run the tool:

```python
        # 4. Our code runs the real function, chosen by the name the model sent.
        # CHANGED: a tool made with @tool is run with .invoke(), passing the arguments dict.
        selected_tool = tools_by_name.get(call["name"])
        if selected_tool is None:
            # The model can ask for a name we never gave it. Tell it, don't crash.
            result = f"Unknown tool: {call['name']}"
        else:
            result = selected_tool.invoke(call["args"])
        print("Tool returned:", result, "\n")
```

| Part | What it does |
|---|---|
| `tools_by_name.get(call["name"])` | Looks the name up, and gives `None` instead of an error when it is missing |
| `if selected_tool is None` | The name was not one of ours |
| `result = f"Unknown tool: ..."` | Puts a sentence in the same place a real result would go |
| `else: ... .invoke(call["args"])` | The normal case, unchanged from Step 6 |

Because the guard sets `result`, the code after it needs no special case. The unknown-tool
message is sent back as a `ToolMessage` like any other result.

## 2. Turn the Result into Text

In the line that sends the result back, wrap it:

```python
        messages.append(ToolMessage(str(result), tool_call_id=call["id"]))
```

## 3. Use the Reference Question

The reference project asks a different question. Change the message:

```python
messages = [HumanMessage("Update the order 4821 to Delivered, arrives Thursday")]
```

The project has one tool, and it can only read. This question asks for a change. That is a
useful thing to run, and Step 9 gives the model a tool that fits it.

## Try it

First, prove the guard works. Temporarily change the question back to
`"Where is my order 4821?"`, and empty the lookup by changing one line:

```python
tools_by_name = {}
```

Run it:

```bash
uv run tool_calling.py
```

```text
User: Where is my order 4821?

Model asks for: get_order_status({'order_id': '4821'})
Tool returned: Unknown tool: get_order_status

AI: I'm sorry, I couldn't look up your order right now.
```

The model still asked for `get_order_status`, which is no longer in the dictionary. The
program did not crash. It told the model, and the model explained. The exact wording of the
last line will differ. Now put back `tools_by_name = {t.name: t for t in tools}` and the
original question.

Then run the reference question:

```bash
uv run tool_calling.py
```

What you see varies, because the model decides. Two outcomes are normal:

| What the model does | What it means |
|---|---|
| Asks for `get_order_status` with order 4821, then tells you the order is still shipped and that it cannot change it | It used the closest tool it has, then was honest about the limit |
| Does not ask for a tool, and says it cannot update orders | It decided no tool fits |

Both are correct. The model can only choose among the tools you give it. To make the update
actually happen you need an update tool, and the lookup you built means adding one is a
single change.

## Checkpoint

<details>
<summary>Full <code>tool_calling.py</code></summary>

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

messages = [HumanMessage("Update the order 4821 to Delivered, arrives Thursday")]
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
        selected_tool = tools_by_name.get(call["name"])
        if selected_tool is None:
            # The model can ask for a name we never gave it. Tell it, don't crash.
            result = f"Unknown tool: {call['name']}"
        else:
            result = selected_tool.invoke(call["args"])
        print("Tool returned:", result, "\n")

        # 5. Send the result back, tagged with the id of the request it answers.
        # CHANGED: ToolMessage replaces {"role": "tool", "tool_call_id": ..., "content": ...}.
        messages.append(ToolMessage(str(result), tool_call_id=call["id"]))

    # 6. Second call: the model reads the result and writes the final answer.
    reply = model_with_tools.invoke(messages)

print("AI:", reply.content)
```

</details>

This is the finished single-question version. Step 8 turns it into the chat version that is
`simple-tool-calling-langchain/tool_calling.py` in the reference project.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `KeyError` on a tool name | Still using `tools_by_name[call["name"]]` | Use `tools_by_name.get(call["name"])` and the `None` check |
| `AttributeError: 'NoneType' object has no attribute 'invoke'` | The `.get` was added but the `if ... is None` check was left out | Add the guard before calling `.invoke` |
| The unknown-tool test still runs the tool | `tools_by_name` was emptied after the loop, or `tools` was changed instead | Change `tools_by_name = {}` on the line where it is built |
| A validation error building the `ToolMessage` | The result was not text and `str(...)` was left out | Wrap the result in `str(result)` |
| The model keeps asking for the missing tool | Only the dictionary was emptied, so the model still has the tool bound | Expected for this test. The guard is what is being tested |

Next: **Step 8 — Keep a Conversation**.
