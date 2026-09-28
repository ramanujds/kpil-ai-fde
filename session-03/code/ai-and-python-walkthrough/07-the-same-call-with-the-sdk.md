# Step 7 — The Same Call With the SDK

> Back to index · Previous: Handling Failures · Next: SDK Error Handling

## Goal

Create `02_sdk_call.py`, which makes the same request as `01_raw_http_call.py` through the
OpenAI Python SDK, and reads the answer, finish reason and token counts from a response
object.

## Why this matters

In Steps 4 to 6 you wrote the URL, the headers, the JSON body, the error checks and the
JSON unpacking yourself. The SDK does all of that. You give it a base URL and a key **once**
when you create a client, and after that a call is one method with named arguments. The
response comes back as an object, so you write `choice.message.content` instead of
`data["choices"][0]["message"]["content"]`, and a typo becomes an editor warning rather than a
runtime `KeyError`.

Two points to keep straight:

- **The SDK is not tied to OpenAI's servers.** It only sends the OpenAI request shape to
  whatever `base_url` you give it. Ollama accepts that shape, so pointing the SDK at Ollama
  just works. This is the payoff of the config file from Step 3.
- **Roles.** This is the first time you use all three: `system` sets the model's behaviour
  and tone, `user` carries the question, and `assistant` holds the model's earlier answers.
  Steps 4 to 6 used only `user`.

## 1. Start the file: docstring and imports

Create `02_sdk_call.py`:

```python
"""
Step 2: The same call, using the official OpenAI Python SDK.

Compare with 01_raw_http_call.py. The request and response are identical;
the SDK just does the plumbing for you:
  - builds the URL and headers
  - turns the reply into an object (response.choices[0]...) instead of a dict
  - raises specific, well-named errors

The SDK works with Ollama too, because Ollama speaks the same API.
Only base_url, api_key and model (all in config.py) change.

Run (from this folder):
    uv run python 02_sdk_call.py
"""

from openai import OpenAI

import config
```

`OpenAI` is the client class. We add `import openai` in Step 8, when we need its exception
classes.

## 2. Create the client once

```python
# ---------------------------------------------------------------
# 1. Create the client once, reuse it for every call
# ---------------------------------------------------------------
client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
    timeout=120,  # seconds
)
```

Create the client **once** and reuse it for every call. `timeout=120` plays the same role as
in the raw version.

## 3. Write the messages

```python
# ---------------------------------------------------------------
# 2. Messages: a conversation as a list of role + content
# ---------------------------------------------------------------
# system    sets the behaviour and tone (the model's "job description")
# user      what the person asks
# assistant what the model said earlier (used when you send a longer chat)
messages = [
    {"role": "system", "content": "You are a friendly teacher. Answer in two short sentences."},
    {"role": "user", "content": "Explain what an API is."},
]
```

The `system` message is your standing instructions to the model. Change its wording and the
tone or length of every answer changes with it.

## 4. Make the call

```python
# ---------------------------------------------------------------
# 3. Make the call
# ---------------------------------------------------------------
response = client.chat.completions.create(
    model=config.MODEL,
    messages=messages,
    temperature=0.2,
    max_tokens=150,  # upper limit on the length of the answer
)
```

Compare this with the raw version: the arguments are the same fields you put in the JSON
body. `max_tokens=150` is new; it caps the answer length, so a rambling model cannot run up
a large bill.

## 5. Read the response

```python
# ---------------------------------------------------------------
# 4. Read the response
# ---------------------------------------------------------------
# Same fields as the raw JSON, now reached with dots instead of brackets.
choice = response.choices[0]
print("Answer:", choice.message.content)
print("Finish reason:", choice.finish_reason)
print("Model that answered:", response.model)

print("\nTokens")
print("  prompt (what we sent):", response.usage.prompt_tokens)
print("  completion (what came back):", response.usage.completion_tokens)
print("  total:", response.usage.total_tokens)
```

The same information as before, reached with dots instead of brackets. `response.usage`
holds the token counts.

## Try it

```bash
uv run python 02_sdk_call.py
```

Expected output (your wording and numbers will differ slightly):

```text
Answer: An API, or Application Programming Interface, is a set of defined rules that enable different software systems to communicate ...
Finish reason: stop
Model that answered: llama3:8b

Tokens
  prompt (what we sent): 34
  completion (what came back): 52
  total: 86
```

Notice the prompt is 34 tokens even though your question is only a few words. The `system`
message and the message structure count too.

## Checkpoint

<details>
<summary>Full <code>02_sdk_call.py</code> after this step</summary>

```python
"""
Step 2: The same call, using the official OpenAI Python SDK.

Compare with 01_raw_http_call.py. The request and response are identical;
the SDK just does the plumbing for you:
  - builds the URL and headers
  - turns the reply into an object (response.choices[0]...) instead of a dict
  - raises specific, well-named errors

The SDK works with Ollama too, because Ollama speaks the same API.
Only base_url, api_key and model (all in config.py) change.

Run (from this folder):
    uv run python 02_sdk_call.py
"""

from openai import OpenAI

import config

# ---------------------------------------------------------------
# 1. Create the client once, reuse it for every call
# ---------------------------------------------------------------
client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
    timeout=120,  # seconds
)

# ---------------------------------------------------------------
# 2. Messages: a conversation as a list of role + content
# ---------------------------------------------------------------
# system    sets the behaviour and tone (the model's "job description")
# user      what the person asks
# assistant what the model said earlier (used when you send a longer chat)
messages = [
    {"role": "system", "content": "You are a friendly teacher. Answer in two short sentences."},
    {"role": "user", "content": "Explain what an API is."},
]

# ---------------------------------------------------------------
# 3. Make the call
# ---------------------------------------------------------------
response = client.chat.completions.create(
    model=config.MODEL,
    messages=messages,
    temperature=0.2,
    max_tokens=150,  # upper limit on the length of the answer
)

# ---------------------------------------------------------------
# 4. Read the response
# ---------------------------------------------------------------
# Same fields as the raw JSON, now reached with dots instead of brackets.
choice = response.choices[0]
print("Answer:", choice.message.content)
print("Finish reason:", choice.finish_reason)
print("Model that answered:", response.model)

print("\nTokens")
print("  prompt (what we sent):", response.usage.prompt_tokens)
print("  completion (what came back):", response.usage.completion_tokens)
print("  total:", response.usage.total_tokens)
```

</details>

The file has no error handling yet, which comes in Step 8.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'openai'` | Ran plain `python`, or skipped `uv sync` | Use `uv run python 02_sdk_call.py` from the project folder |
| `openai.APIConnectionError` with a long trace | Ollama is not running, or `base_url` is wrong | Start Ollama and check the base URL. Step 8 makes this a short message |
| `TypeError` about an unexpected argument | A typo in a keyword such as `max_token` | The name is `max_tokens`, and the others are `model`, `messages`, `temperature` |
| `AttributeError: 'NoneType' object has no attribute 'prompt_tokens'` | Some servers leave out the usage section | Guard with `if response.usage:` before reading it |

Next: **Step 8 — SDK Error Handling**.
