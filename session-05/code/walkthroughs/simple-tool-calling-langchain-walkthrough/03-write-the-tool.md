# Step 3 — Write the Tool

> Back to index · Previous: Project Setup · Next: Give the Tool to the Model

## Goal

Write `get_order_status` as a LangChain tool, and see what LangChain builds from it without
you writing a description by hand.

## Why this matters

In the plain-SDK project the tool came in two pieces: the Python function, and a separate
nested dictionary that described it to the model. Two pieces means two places to keep in
step. Rename an input in one and forget the other, and the model sends a name your function
does not have.

`@tool` joins the pieces. LangChain reads three things from the function itself: its name,
its type hints and its docstring. It builds the description from them. The docstring is not a
comment for humans any more. **It is what the model reads**, so it must say when to use the
tool and when not to.

A side effect to know about: once decorated, `get_order_status` is no longer a plain
function. It is a tool object. You run it with `.invoke(...)`, not by calling it like a
function. That object is what carries the name and description to the model in Step 4.

## 1. The Import and the Order Table

Create `tool_calling.py`:

```python
from langchain_core.tools import tool

# A fake order table shared by all the tools.
orders = {
    "4821": "Shipped, arrives Thursday",
    "4822": "Packed, ships tomorrow",
}
```

The table sits at the top of the file, outside the function. In the plain version it was
inside. Moving it out means later tools can share it.

## 2. The Tool

```python
# 1. The tools: plain Python functions. The model never runs these, our code does.
# CHANGED: the @tool line replaces the whole hand-written tool description.
# LangChain builds it from the function name, the type hints (order_id: str) and the
# docstring below. The docstring is what the model reads, so say when to use it.
@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."""
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")
```

| Part | What LangChain does with it |
|---|---|
| `get_order_status` | Becomes the tool's name, the text the model sends back to ask for it |
| `order_id: str` | Becomes the input: its name, and its type (text) |
| The docstring | Becomes the tool's description |
| `-> str` | Not sent to the model. It is for you and your editor |

The "not found" message is a full sentence, not an error. The model passes it on to the
customer, so it should read well to one.

## Try it

Import the tool without running anything else and look at what LangChain made:

```bash
uv run python -c "from tool_calling import get_order_status as t; print(t.name); print(t.description); print(t.args)"
```

```text
get_order_status
Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds.
{'order_id': {'title': 'Order Id', 'type': 'string'}}
```

Those three lines are everything the model will know about this tool. Now run the tool:

```bash
uv run python -c "from tool_calling import get_order_status as t; print(t.invoke({'order_id': '4821'})); print(t.invoke({'order_id': '9999'}))"
```

```text
Shipped, arrives Thursday
No order found with number 9999. Check the number and try again.
```

Notice that `.invoke` takes a dictionary of inputs, keyed by name. The model's request in
Step 4 arrives in exactly that shape, which is why it can be passed straight in.

## Checkpoint

<details>
<summary>Full <code>tool_calling.py</code> after this step</summary>

```python
from langchain_core.tools import tool

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
```

</details>

This is an intermediate version and does not match the reference yet.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `TypeError: 'StructuredTool' object is not callable` | You called `get_order_status("4821")` like a function | Use `get_order_status.invoke({"order_id": "4821"})` |
| An error that the tool needs a description | The docstring is missing, so there is nothing to build the description from | Add the docstring directly under the `def` line |
| A validation error from `.invoke` | You passed `"4821"` instead of `{"order_id": "4821"}` | Pass a dictionary keyed by input name |
| `ModuleNotFoundError: tool_calling` | You ran the command from another folder | `cd` into the project folder first |

Next: **Step 4 — Give the Tool to the Model**.
