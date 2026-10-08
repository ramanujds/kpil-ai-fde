# Step 8 — Keep a Conversation

> Back to index · Previous: Handle an Unknown Tool · Next: Add a Cancel Tool

## Goal

Turn the one-question script into a chat that reads questions from the user and remembers the
conversation, and run it against a local Ollama model.

## Why this matters

Up to Step 7 the program asked one hardcoded question, answered it and stopped. A real
assistant is a conversation. The user asks, reads the answer, and asks again, often with a
follow-up like "and what about 4822?" that only makes sense if the assistant remembers the
last turn.

The model remembers nothing. Every call to `invoke` is independent. The only memory it has is
the list of messages you send it, so the memory is a list in your code. You keep one list for
the whole conversation, add every new message to it, and send all of it each time. That
includes the model's own tool requests and your `ToolMessage` results. Leave one out and the
next call fails, or the model forgets what it just did.

Two smaller changes come with this step.

- **A system message.** It is the first message in the list and sets the ground rules. Here
  it solves a real problem. A small model with tools attached often treats the tool list as
  the only thing it is allowed to do. Ask it something no tool covers, and it replies "I have
  no function for that" instead of just answering. The system message tells it to use a tool
  only when one clearly fits, and to answer directly otherwise.
- **A local model.** The reference project now runs `llama3.1:8b` through Ollama, so it needs
  no paid key. Ollama speaks the same API as OpenAI, which is why the same `ChatOpenAI` class
  works. You only change where it points.

## 1. Point the Model at Ollama

If Ollama is not set up on your machine yet, do the Ollama setup from the earlier Day 3
material first, then pull the model:

```bash
ollama pull llama3.1:8b
```

Replace the model line:

```python
model = ChatOpenAI(model="llama3.1:8b", base_url="http://localhost:11434/v1",
    api_key="ollama")
```

| Part | What it does |
|---|---|
| `model="llama3.1:8b"` | The Ollama model name, not an OpenAI one |
| `base_url="http://localhost:11434/v1"` | Sends the calls to Ollama on your machine |
| `api_key="ollama"` | A dummy value. Ollama ignores it, but the client insists on one |

`load_dotenv()` can stay. It does no harm, and the project still carries a `.env.example`.

## 2. Replace the Single Question with a History

Delete the lines that build `messages` and print the question. In their place, create the
history with the system message in it:

```python
history = [
    SystemMessage(
        "You are a helpful assistant. Use a tool only when one clearly matches the request. "
        "For general questions, or requests no tool can do, answer directly in plain text "
        "from your own knowledge, or say politely what you cannot do. "
        "Never mention functions or tools to the user."
    ),
]
```

Add `SystemMessage` to the import line:

```python
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
```

## 3. Read Questions in a Loop

Everything from here to the end of the file goes inside a `while True` loop. Start it with the
part that reads the user:

```python
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
```

| Part | What it does |
|---|---|
| `input("You: ").strip()` | Waits for the user to type a line |
| `except (EOFError, KeyboardInterrupt)` | Ctrl+D or Ctrl+C ends the chat quietly instead of printing a traceback |
| `if not user_input: continue` | An empty line asks again |
| `exit` or `quit` | Leaves the loop |
| `history.append(HumanMessage(...))` | The new question joins the memory |
| `model_with_tools.invoke(history)` | The model sees the whole conversation, not just the last line |

## 4. Let the Model Ask for Tools More Than Once

Change `if reply.tool_calls:` to `while reply.tool_calls:`, move the second `invoke` to the end
of that block, and send `history` instead of `messages`. The tool part now reads:

```python
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
```

An `if` allowed exactly one round of tools. A `while` keeps going while the model keeps
asking. After the tool results go back, the model either answers, which ends the loop, or asks
for another tool, which runs the block again. The tool output is printed in square brackets
so the room can tell a tool call from an ordinary answer.

## 5. Save the Answer and Trim the Comments

After the `while` block, still inside the outer loop:

```python
    history.append(reply)
    print("AI:", reply.content, "\n")
```

Saving the answer is what lets the next question build on it.

The reference file also drops the numbered and `CHANGED:` comments. They helped while
comparing with the plain SDK version and they have done their job. Keep them if you like.
Comments do not change what the program does.

## Try it

```bash
uv run tool_calling.py
```

```text
Chat started. Type 'exit' to quit.

You: Where is order 4821?
  [Model asks for: get_order_status({'order_id': '4821'})]
  [Tool returned: Shipped, arrives Thursday]
AI: Order 4821 has shipped and should arrive on Thursday.

You: What is the capital of France?
AI: The capital of France is Paris.

You: What was the first thing I asked you?
AI: You asked where order 4821 was.

You: exit
```

Three things to point at. The first question uses the tool. The second does not, and the
model answers from its own knowledge. The third is answered from the history, with no tool
and no new information. Wording will differ on your run.

## Checkpoint

<details>
<summary>Full <code>tool_calling.py</code></summary>

```python
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(model="llama3.1:8b", base_url="http://localhost:11434/v1",
    api_key="ollama")

# A fake order table used by the tool.
orders = {
    "4821": "Shipped, arrives Thursday",
    "4822": "Packed, ships tomorrow",
}


# The model never runs this, our code does. LangChain builds the tool description
# from the name, the type hints and the docstring, so the docstring says when to use it.
@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."""
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


tools = [get_order_status]
model_with_tools = model.bind_tools(tools)

# Name -> tool lookup, so the loop works for any tool added to the list above.
tools_by_name = {t.name: t for t in tools}

# The full history is sent on every call, so the model remembers earlier turns.
# The system message tells it to answer directly when no tool fits.
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

    # While the model asks for tools, run them and send the results back.
    while reply.tool_calls:
        history.append(reply)

        for call in reply.tool_calls:
            print(f"  [Model asks for: {call['name']}({call['args']})]")

            selected_tool = tools_by_name.get(call["name"])
            if selected_tool is None:
                # The model can ask for a name we never gave it. Tell it, don't crash.
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

This matches `simple-tool-calling-langchain/tool_calling.py` in the reference project exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Connection refused` on the first question | Ollama is not running | Start Ollama, then run `ollama list` to confirm `llama3.1:8b` is there |
| The model forgets earlier questions | `messages` or a fresh list was sent, not `history` | Send `history` on every `invoke` |
| A 400 error after a tool call | The model's reply or a `ToolMessage` was not added to `history` | Append `reply` before the `for` loop and a `ToolMessage` for every call |
| The model answers "I have no function for that" | The system message is missing | Put the `SystemMessage` first in `history` |
| `NameError: SystemMessage` | The import line was not updated | Add `SystemMessage` to the `langchain_core.messages` import |

Next: **Step 9 — Add a Cancel Tool**.
