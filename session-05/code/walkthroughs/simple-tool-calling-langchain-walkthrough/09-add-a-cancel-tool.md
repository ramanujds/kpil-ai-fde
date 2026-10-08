# Step 9 — Add a Cancel Tool

> Back to index · Previous: Keep a Conversation · Next: Ask a Human First

## Goal

Add a second tool, `cancel_order`, that changes the order table, and see what happens when
nothing stands between the model's request and the change.

## Why this matters

`get_order_status` only reads. If the model calls it by mistake, nothing is lost. The customer
gets an answer they did not need.

`cancel_order` writes. If the model calls it by mistake, a real order is gone. The model
decides which tool to call from the user's words and the tool's docstring, and models
misread things. "I might cancel order 4821 if it is late" is not an instruction to cancel,
but a model can still take it as one.

This step builds the tool and runs it with no safeguard on purpose. It is faster to see why
Step 10 is needed by watching the order disappear than by being told. It also shows the
payoff of Step 6: a new tool is one function and one entry in a list. The loop does not change.

## 1. Start a New File

The approval version is a separate script, so the plain chat from Step 8 stays as it is:

```bash
cp tool_calling.py human_in_the_loop.py
```

Do the rest of this step and the next one in `human_in_the_loop.py`.

## 2. Write the Tool

Add this below `get_order_status`:

```python
@tool
def cancel_order(order_id: str) -> str:
    """Cancel an order. Use only when the customer clearly asks to cancel an order."""
    if order_id not in orders:
        return f"No order found with number {order_id}. Check the number and try again."
    orders[order_id] = "Cancelled"
    return f"Order {order_id} has been cancelled."
```

Two details matter. The docstring says when to use it, and it says `only when the customer
clearly asks`. That wording pushes the model away from the "I might cancel" case, but it is a
nudge, not a guarantee. And the function checks that the order exists before changing
anything, then returns a sentence either way, so the model always has something to report.

Shorten the `get_order_status` docstring to match, since the "Do not use for refunds" sentence
is no longer needed:

```python
    """Look up the delivery status of an order. Use when the customer asks where their order is."""
```

## 3. Give Both Tools to the Model

```python
tools = [get_order_status, cancel_order]
```

Nothing else changes. `bind_tools` and `tools_by_name` are both built from this list.

## Try it

```bash
uv run human_in_the_loop.py
```

```text
Chat started. Type 'exit' to quit.

You: Cancel order 4821
  [Model asks for: cancel_order({'order_id': '4821'})]
  [Tool returned: Order 4821 has been cancelled.]
AI: Your order 4821 has been cancelled.

You: Where is order 4821?
  [Model asks for: get_order_status({'order_id': '4821'})]
  [Tool returned: Cancelled]
AI: Order 4821 has been cancelled.

You: exit
```

Nobody was asked. The model proposed a cancellation and the code carried it out, and the
second question proves the change stuck. For a demo order that is harmless. For a real order,
or a refund, or a message sent to a customer, it is not.

## Checkpoint

<details>
<summary>Full <code>human_in_the_loop.py</code> at this point</summary>

```python
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(model="llama3.1:8b", base_url="http://localhost:11434/v1",
    api_key="ollama")

# A fake order table used by the tools.
orders = {
    "4821": "Shipped, arrives Thursday",
    "4822": "Packed, ships tomorrow",
}


@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of an order. Use when the customer asks where their order is."""
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


@tool
def cancel_order(order_id: str) -> str:
    """Cancel an order. Use only when the customer clearly asks to cancel an order."""
    if order_id not in orders:
        return f"No order found with number {order_id}. Check the number and try again."
    orders[order_id] = "Cancelled"
    return f"Order {order_id} has been cancelled."


tools = [get_order_status, cancel_order]
model_with_tools = model.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}

history = [
    SystemMessage(
        "You are a helpful assistant. Use a tool only when one clearly matches the request. "
        "For general questions, or requests no tool can do, answer directly in plain text "
        "from your own knowledge, or say politely what you cannot do. "
        "Never mention functions or tools to the user."
    ),
]


print("Chat started. Type 'exit' to quit.\n")

while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit"):
        break

    history.append(HumanMessage(user_input))
    reply = model_with_tools.invoke(history)

    while reply.tool_calls:
        history.append(reply)

        for call in reply.tool_calls:
            print(f"  [Model asks for: {call['name']}({call['args']})]")

            selected_tool = tools_by_name.get(call["name"])
            if selected_tool is None:
                result = f"Unknown tool: {call['name']}"
            else:
                result = selected_tool.invoke(call["args"])
            print(f"  [Tool returned: {result}]")

            history.append(ToolMessage(str(result), tool_call_id=call["id"]))

        reply = model_with_tools.invoke(history)

    history.append(reply)
    print("AI:", reply.content, "\n")
```

</details>

This is not the final file yet. Step 10 adds the approval.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| The model never cancels | The docstring is vague, or the tool is missing from `tools` | Check the `tools` list and the "Use only when" sentence |
| The model cancels when the user was only thinking aloud | The docstring is a nudge, not a rule | This is the reason for Step 10 |
| `cancel_order` is called but nothing changes in the next question | The program was restarted, and `orders` is rebuilt from the top | Expected. The table lives in memory only |
| `KeyError` on an order number | The `order_id not in orders` check was left out | Add the check before changing the table |

Next: **Step 10 — Ask a Human First**.
