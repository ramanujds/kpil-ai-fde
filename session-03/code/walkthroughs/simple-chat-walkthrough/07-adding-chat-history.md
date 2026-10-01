# Step 7 — Adding Chat History

> Back to index · Previous: The OpenAI Version · Next: Recap and Exercises

## Goal

Create `chat_with_history.py`, a copy of `chat.py` that remembers the conversation by
keeping every question and answer in a list and sending the whole list each turn.

## Why this matters

The model never remembers anything. A chat website seems to remember you only because it
sends the whole conversation again with every new message. Memory is not a feature of the
model. It is a list that your code keeps.

Two details matter. The list must live outside the loop, or it would be emptied every turn.
And the model's own answers must go in the list too, otherwise the model sees only your side
of the conversation.

## 1. Start from `chat.py`

```bash
cp chat.py chat_with_history.py
```

On Windows PowerShell use `Copy-Item chat.py chat_with_history.py`. The imports, the client
and `MODEL` stay as they are.

## 2. Create the History Before the Loop

Add below `MODEL = "llama3:8b"`:

```python
# The chat history. It lives outside the loop, so it keeps growing.
messages = []
```

Placed here, the list is created once. If you put it inside the `while` loop, it would be
reset every turn and you would be back to no memory.

## 3. Add the Question to the History

Inside the loop, after the quit check, add:

```python
    # Add the user's question to the history.
    messages.append({"role": "user", "content": user_input})
```

`append` adds one message to the end of the list, using the same `role` and `content` shape
as before.

## 4. Send the Whole History

Replace the model call, including its old comment, with:

```python
    # Send the whole history, not just the latest question.
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    answer = response.choices[0].message.content
```

The one-item list `[{"role": "user", ...}]` is now just `messages`. The answer is kept in a
variable because it is used twice, once to store and once to print.

## 5. Add the Answer to the History

```python
    # Add the model's answer to the history too.
    messages.append({"role": "assistant", "content": answer})

    print("AI:", answer, "\n")
```

The role is `assistant`, which marks the message as the model's own words. On the next turn
the model reads the whole conversation, both sides, and answers in that context.

## Try it

```bash
uv run chat_with_history.py
```

```text
Chat with llama3:8b. Type 'quit' to exit.

You: My name is Asha
AI: Nice to meet you, Asha!

You: What is my name?
AI: Your name is Asha!

You: quit
```

The same two questions that failed in Step 4 now work. To see why, add
`print(messages)` just before the model call and run two turns. On the second turn the list
holds three messages: your first question, the first answer and your second question.

## Checkpoint

<details>
<summary>Full <code>chat_with_history.py</code></summary>

```python
from openai import OpenAI

# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"

# The chat history. It lives outside the loop, so it keeps growing.
messages = []

print("Chat with llama3:8b. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # Add the user's question to the history.
    messages.append({"role": "user", "content": user_input})

    # Send the whole history, not just the latest question.
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    answer = response.choices[0].message.content

    # Add the model's answer to the history too.
    messages.append({"role": "assistant", "content": answer})

    print("AI:", answer, "\n")
```

</details>

This matches the reference project's `chat_with_history.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| The model still forgets | `messages = []` is inside the loop | Move it above `while True:` |
| The model repeats itself or seems confused | The answer was never appended as `assistant` | Add the `assistant` append after each reply |
| The model ignores your first message | Sent `[...]` with only the new question | Pass `messages=messages` |
| Replies get slower in a long chat | The whole history is re-sent every turn | Expected. Trimming old messages is a later topic |

Next: **Step 8 — Recap and Exercises**.
