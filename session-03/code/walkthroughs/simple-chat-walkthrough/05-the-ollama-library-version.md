# Step 5 — The Ollama Library Version

> Back to index · Previous: The Chat Loop · Next: The OpenAI Version

## Goal

Create `chat_ollama.py`, the same chat app written with Ollama's own Python library.

## Why this matters

Ollama offers two doors to the same model. The OpenAI-style door in `chat.py` is useful
because the same code can later point at OpenAI. The Ollama-style door is shorter, because
Ollama's library already knows where Ollama lives.

Seeing both side by side shows that the app is not tied to one SDK. What matters is the
idea: a model name, a list of messages, and an answer.

## 1. Import

Create `chat_ollama.py`:

```python
import ollama

MODEL = "llama3:8b"
```

There is no client object and no address. The library assumes Ollama is on your computer.

## 2. Copy the Loop

```python
print("Chat with llama3:8b using the Ollama library. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break
```

This is the same as Step 4, apart from the greeting.

## 3. Call the Model

```python
    # Only the current question is sent. The model remembers nothing.
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
    )

    print("AI:", response.message.content, "\n")
```

Two differences from `chat.py`. The call is `ollama.chat(...)`, and the answer is read from
`response.message.content` instead of `response.choices[0].message.content`.

## Try it

```bash
uv run chat_ollama.py
```

```text
Chat with llama3:8b using the Ollama library. Type 'quit' to exit.

You: My name is Asha
AI: Nice to meet you, Asha!

You: What is my name?
AI: I'm just an AI, I don't have any information about your name.

You: quit
```

Same behaviour, same lack of memory.

## Checkpoint

<details>
<summary>Full <code>chat_ollama.py</code></summary>

```python
import ollama

MODEL = "llama3:8b"

print("Chat with llama3:8b using the Ollama library. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # Only the current question is sent. The model remembers nothing.
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
    )

    print("AI:", response.message.content, "\n")
```

</details>

This matches the reference project's `chat_ollama.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ConnectionError` mentioning Ollama | Ollama is not running | Start the Ollama app |
| `AttributeError: ... has no attribute 'choices'` | Used the OpenAI-style answer path | Read `response.message.content` |
| `ModuleNotFoundError: ollama` | Ran outside the uv environment | Use `uv run chat_ollama.py` |

Next: **Step 6 — The OpenAI Version**.
