# Step 6 — The OpenAI Version

> Back to index · Previous: The Ollama Library Version · Next: Adding Chat History

## Goal

Create `chat_openai.py`, the same app calling OpenAI's `gpt-4o-mini`, with the API key kept
in a `.env` file that Git ignores.

## Why this matters

A hosted model costs money and is protected by a secret key. Anyone who has the key can
spend your quota. So the one new skill in this step is not the model call, which you
already know. It is handling a secret: keep it out of the code, keep it out of Git, and
share only a template with a fake value.

## 1. Create the Template `.env.example`

```text
OPENAI_API_KEY=your-openai-api-key-here
```

This file is safe to commit because the value is fake. It tells other people which setting
the app needs.

## 2. Create Your Real `.env`

```bash
cp .env.example .env
```

On Windows PowerShell use `Copy-Item .env.example .env`. Open `.env` and replace the fake
value with your real key. Confirm Git will ignore it:

```bash
git check-ignore .env
```

It should print `.env`. If it prints nothing, stop and check `.gitignore` from Step 2.
Never put a real key in `.env.example`.

## 3. Load the Key and Create the Client

Create `chat_openai.py`:

```python
from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"
```

`load_dotenv()` copies the lines of `.env` into the environment. `OpenAI()` with no
arguments looks for `OPENAI_API_KEY` there, so the key never appears in the code. There is
no `base_url` because the library defaults to OpenAI's servers.

## 4. The Same Loop

```python
print("Chat with OpenAI's gpt-4o-mini. Type 'quit' to exit.\n")

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

The loop and the call are identical to `chat.py`. Only the client changed.

## Try it

```bash
uv run chat_openai.py
```

```text
Chat with OpenAI's gpt-4o-mini. Type 'quit' to exit.

You: My name is Asha
AI: Nice to meet you, Asha! How can I assist you today?

You: What is my name?
AI: I don't know your name. If you'd like to share it, feel free!

You: quit
```

A hosted model forgets just like the local one. Memory is something your code adds, not
something the model has.

## Checkpoint

<details>
<summary>Full <code>chat_openai.py</code></summary>

```python
from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"

print("Chat with OpenAI's gpt-4o-mini. Type 'quit' to exit.\n")

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

<details>
<summary>Full <code>.env.example</code></summary>

```text
OPENAI_API_KEY=your-openai-api-key-here
```

</details>

These match the reference project's `chat_openai.py` and `.env.example` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Missing credentials ... OPENAI_API_KEY` | No `.env` file, or it is in a different folder | Create `.env` next to `chat_openai.py` |
| `401 Incorrect API key` | Typo, extra quotes or spaces in the key | Re-copy the key into `.env` with no quotes |
| `429` rate limit or quota error | Free tier or credit limit reached | Wait, or check usage on your provider account |
| `.env` shows up in `git status` | `.gitignore` is missing the line | Add `.env` to `.gitignore` before committing |

Next: **Step 7 — Adding Chat History**.
