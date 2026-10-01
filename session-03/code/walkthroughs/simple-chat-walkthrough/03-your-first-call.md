# Step 3 — Your First Call

> Back to index · Previous: Project Setup · Next: The Chat Loop

## Goal

Send one hard-coded question to `llama3:8b` and print the answer. No loop and no typing
yet, just proof that Python can talk to the model.

## Why this matters

Beginners often build the loop, the input and the model call all at once, and then cannot
tell which part is broken. Getting a single call working first means every later problem is
a problem with the new thing you just added.

This step also shows what a request really is: a model name and a list of messages. Nothing
else is hidden.

## 1. Import and Create the Client

Create `chat.py`:

```python
from openai import OpenAI

# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"
```

The client is the object that knows where to send requests. `base_url` points it at Ollama
on your own computer instead of at OpenAI. Port 11434 is where Ollama listens.

## 2. Send a Question

Add below:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
```

`messages` is a list. Each item is a dict with a `role` and the `content`. Here there is one
item, from the `user`.

## 3. Print the Answer

```python
print(response.choices[0].message.content)
```

The response holds a list called `choices`. You asked for one answer, so you take the first,
`choices[0]`, then read its message text.

## Try it

```bash
uv run chat.py
```

```text
The capital of France is Paris.
```

Change the question in the file, save, and run it again. The wording of the answer may
vary between runs.

## Checkpoint

<details>
<summary>Full <code>chat.py</code> after this step</summary>

```python
from openai import OpenAI

# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)

print(response.choices[0].message.content)
```

</details>

This is an intermediate version. Step 4 turns it into the final `chat.py`.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Connection error` | Ollama is not running | Start Ollama and rerun |
| `model 'llama3:8b' not found` | The model was never downloaded | `ollama pull llama3:8b` |
| `ModuleNotFoundError: openai` | Ran with plain `python` outside the environment | Use `uv run chat.py` |

Next: **Step 4 — The Chat Loop**.
