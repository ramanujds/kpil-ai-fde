# Step 4 — Give the Tool to the Model

> Back to index · Previous: Write the Tool · Next: Run the Tool and Return the Result

## Goal

Create the model object, attach the tool to it once, send the first question, and read the
model's request for a tool.

## Why this matters

In the plain-SDK project you passed `tools=tools` on every call to the model. Forget it on
the second call and the model quietly loses its tools. `bind_tools` fixes this by returning a
new model object that already carries the tool list. Every call to that object includes the
tools, with nothing to remember.

`invoke` is LangChain's one word for "run this with this input". Here it replaces
`client.chat.completions.create(...)`, and it takes the list of messages directly. Messages
are small classes now: `HumanMessage` for the user's text. The `{"role": "user", ...}`
dictionary is gone.

This step stops after the first call on purpose. You will see the model's reply as raw
data, before any code acts on it. That reply is the most surprising thing in the whole
program, and worth looking at once without anything else going on.

## 1. The Imports, the Key and the Model

Replace the single import line at the top, and add the key loading and the model between the
imports and the order table:

```python
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# Reads OPENAI_API_KEY from the .env file. ChatOpenAI picks it up automatically.
load_dotenv()

# CHANGED: one LangChain model object replaces the OpenAI client.
model = ChatOpenAI(model="gpt-4o-mini")
```

`load_dotenv()` puts the key into the environment. `ChatOpenAI` finds it there on its own,
so you never pass the key in code.

## 2. Bind the Tool

After the tool, add:

```python
# 2. Give the tools to the model.
# CHANGED: bind_tools() replaces passing tools=tools on every call.
model_with_tools = model.bind_tools([get_order_status])
```

`model_with_tools` is the object you call from now on. The plain `model` is not used again.

## 3. Ask the Question

```python
messages = [HumanMessage("Where is my order 4821?")]
print("User:", messages[0].content, "\n")

# 3. First call: the model sees the question and the tools.
# CHANGED: invoke() replaces client.chat.completions.create(...).
reply = model_with_tools.invoke(messages)
print("Text:", repr(reply.content))
print("Tool calls:", reply.tool_calls)
```

The two `print` lines at the end are temporary. They let you look at the reply. Step 5
replaces them.

## Try it

```bash
uv run tool_calling.py
```

```text
User: Where is my order 4821?

Text: ''
Tool calls: [{'name': 'get_order_status', 'args': {'order_id': '4821'}, 'id': 'call_...', 'type': 'tool_call'}]
```

The `id` is a long generated string and will differ on every run.

Read the two lines slowly. The model wrote **no text at all**, only a request: the tool's
name, the arguments it chose, and an id. Compare with the plain SDK, where the arguments
arrived as JSON text and needed `json.loads`. Here `args` is already a dictionary.

## Checkpoint

<details>
<summary>Full <code>tool_calling.py</code> after this step</summary>

```python
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
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
print("Text:", repr(reply.content))
print("Tool calls:", reply.tool_calls)
```

</details>

This is an intermediate version and does not match the reference yet.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `openai.AuthenticationError` (a 401) | The key is missing, wrong, or `.env` is not in the folder you ran from | Check `.env` for `OPENAI_API_KEY=` and run from the project folder |
| `Tool calls: []` and the text answers the question | The model did not use the tool. Run it again, or check the docstring says when to use it | Keep the "Use when" sentence in the docstring |
| `AttributeError: 'ChatOpenAI' object has no attribute 'tool_calls'` | You called `model.invoke` and then used `model`, or confused `model` with the reply | Call `model_with_tools.invoke(messages)` and read `tool_calls` on the reply |
| The model ignores the tool every time | You invoked `model`, not `model_with_tools` | Use `model_with_tools` for the call |

Next: **Step 5 — Run the Tool and Return the Result**.
