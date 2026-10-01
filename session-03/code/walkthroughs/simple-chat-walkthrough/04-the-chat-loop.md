# Step 4 — The Chat Loop

> Back to index · Previous: Your First Call · Next: The Ollama Library Version

## Goal

Turn the single call into a chat: read a question from the keyboard, answer it, repeat, and
stop when the user types `quit`.

## Why this matters

A loop is all that separates a script from a chat. But look closely at what goes inside it:
a brand new `messages` list is built every turn, holding only the latest question. That is
why the app has no memory, and it is the exact line you will change in the next lesson.

Building the "no memory" version carefully, and then proving it forgets, makes the later
fix feel obvious rather than magical.

## 1. Add a Greeting and the Loop

Replace everything below `MODEL = "llama3:8b"` with:

```python
print("Chat with llama3:8b. Type 'quit' to exit.\n")

while True:
```

`while True` repeats forever, until something inside uses `break`.

## 2. Read the Question and Allow Quitting

Inside the loop, indented:

```python
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break
```

`input()` waits for the user to type and press Enter. `.lower()` makes `QUIT` and `Quit`
work too. `break` leaves the loop and the program ends.

## 3. Send the Question and Print the Answer

Still inside the loop:

```python
    # Only the current question is sent. The model remembers nothing.
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
    )

    print("AI:", response.choices[0].message.content, "\n")
```

The hard-coded question is now the variable `user_input`. The trailing `"\n"` adds a blank
line between turns so the chat is easier to read.

## Try it

```bash
uv run chat.py
```

Prove that it has no memory:

```text
Chat with llama3:8b. Type 'quit' to exit.

You: My name is Asha
AI: Nice to meet you, Asha!

You: What is my name?
AI: I'm afraid I don't know your name! Each time you interact with me, it's a new conversation.

You: quit
```

The model's own words will differ, but it cannot know the name. The second request
contained only "What is my name?".

## Checkpoint

<details>
<summary>Full <code>chat.py</code></summary>

```python
from openai import OpenAI

# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"

print("Chat with llama3:8b. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # Only the current question is sent. The model remembers nothing.
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
    )

    print("AI:", response.choices[0].message.content, "\n")
```

</details>

This matches the reference project's `chat.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `IndentationError` | The loop body is not indented by four spaces | Indent every line inside `while True:` |
| The program never stops | No `break` reached, or the quit check is outside the loop | Keep the `if ... break` inside the loop |
| `EOFError` traceback | Input ended without `quit` (Ctrl+D or piped input) | Expected in this basic version; use `quit` |
| Model "forgets" earlier turns | That is how this version works | Not a bug. Memory comes next lesson |

Next: **Step 5 — The Ollama Library Version**.
