# Step 4 — Building the Request

> Back to index · Previous: Configuration · Next: Sending and Reading the Response

## Goal

Create `01_raw_http_call.py` and build the three parts of an LLM request, the URL, the
headers and the JSON body, then print the body without sending anything yet.

## Why this matters

Every LLM SDK, framework and "AI app" ends up doing the same thing: sending a small piece of
JSON to a URL. If you only ever meet that JSON through library calls, it stays a black box,
and when something goes wrong (a 404, a rejected key, an answer that is cut short) you have
nothing to reason with.

Building the request by hand, and **looking at it before it is sent**, makes the whole
conversation concrete. The body is just a dict: a model name, a list of messages and a
temperature. The key travels in a header, separate from the body, so it is never mixed into
the content. Once you have seen this, an SDK's `create(...)` call is easy to read: its
arguments are these same fields.

## 1. Start the file: docstring and imports

Create `01_raw_http_call.py`. The docstring at the top is documentation for whoever opens the
file next.

```python
"""
Step 1: Call an LLM with plain HTTP.

No LLM library here, only an ordinary web request. The point is to SEE what
travels over the wire, because every SDK and framework does exactly this
underneath.

    Your Python  --POST request (JSON)-->  model server  (Ollama or OpenAI)
    Your Python  <--response (JSON)------  model server

Run (from this folder):
    uv sync
    uv run python 01_raw_http_call.py
"""

import json

import config
```

We import `json` only to print nicely, and `config` from Step 3 for the settings. The HTTP
library comes in the next step, when we actually need it.

## 2. The address

```python
# ---------------------------------------------------------------
# 1. The address: base URL + the "chat completions" path
# ---------------------------------------------------------------
url = f"{config.BASE_URL}/chat/completions"
```

The base URL from config plus the path `/chat/completions`. For Ollama this becomes
`http://localhost:11434/v1/chat/completions`.

## 3. The headers

```python
# ---------------------------------------------------------------
# 2. Headers: metadata about the request
# ---------------------------------------------------------------
# Authorization carries the API key ("Bearer" is just the word the API expects).
# Content-Type says the body is JSON.
headers = {
    "Authorization": f"Bearer {config.API_KEY}",
    "Content-Type": "application/json",
}
```

`Authorization: Bearer <key>` is how most hosted APIs identify you. Ollama accepts any value,
but sending the header anyway means the same code works unchanged against a hosted provider.

## 4. The body

```python
# ---------------------------------------------------------------
# 3. The body: what we are asking
# ---------------------------------------------------------------
# It is a plain dict (see 03_dicts.py in python-essentials).
payload = {
    "model": config.MODEL,
    # messages is a list of dicts, each with a role and its content.
    "messages": [
        {"role": "user", "content": "Explain what an API is in two short sentences."},
    ],
    # temperature controls randomness: 0 = steady and repeatable, higher = more varied.
    "temperature": 0.2,
}
```

`messages` is a list of dicts, each with a `role` and `content`. Here there is one message
from the `user`. Lower the temperature for steady answers, raise it for more variety.

## 5. Print it

```python
print(f"Sending request to {url}")
print("Request body:")
print(json.dumps(payload, indent=2))
```

`json.dumps(payload, indent=2)` turns the dict into readable, indented JSON. This is exactly
what will be sent over the network.

## Try it

```bash
uv run python 01_raw_http_call.py
```

Expected output. Nothing is sent yet, so this works even if Ollama is stopped:

```text
Sending request to http://localhost:11434/v1/chat/completions
Request body:
{
  "model": "llama3:8b",
  "messages": [
    {
      "role": "user",
      "content": "Explain what an API is in two short sentences."
    }
  ],
  "temperature": 0.2
}
```

## Checkpoint

<details>
<summary>Full <code>01_raw_http_call.py</code> after this step</summary>

```python
"""
Step 1: Call an LLM with plain HTTP.

No LLM library here, only an ordinary web request. The point is to SEE what
travels over the wire, because every SDK and framework does exactly this
underneath.

    Your Python  --POST request (JSON)-->  model server  (Ollama or OpenAI)
    Your Python  <--response (JSON)------  model server

Run (from this folder):
    uv sync
    uv run python 01_raw_http_call.py
"""

import json

import config

# ---------------------------------------------------------------
# 1. The address: base URL + the "chat completions" path
# ---------------------------------------------------------------
url = f"{config.BASE_URL}/chat/completions"

# ---------------------------------------------------------------
# 2. Headers: metadata about the request
# ---------------------------------------------------------------
# Authorization carries the API key ("Bearer" is just the word the API expects).
# Content-Type says the body is JSON.
headers = {
    "Authorization": f"Bearer {config.API_KEY}",
    "Content-Type": "application/json",
}

# ---------------------------------------------------------------
# 3. The body: what we are asking
# ---------------------------------------------------------------
# It is a plain dict (see 03_dicts.py in python-essentials).
payload = {
    "model": config.MODEL,
    # messages is a list of dicts, each with a role and its content.
    "messages": [
        {"role": "user", "content": "Explain what an API is in two short sentences."},
    ],
    # temperature controls randomness: 0 = steady and repeatable, higher = more varied.
    "temperature": 0.2,
}

print(f"Sending request to {url}")
print("Request body:")
print(json.dumps(payload, indent=2))
```

</details>

The file is not finished yet. It gains the HTTP call in Step 5 and error handling in Step 6.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'config'` | Running the script from a different folder than the one holding `config.py` | Run it from the project folder with `uv run python 01_raw_http_call.py` |
| `AttributeError: module 'config' has no attribute 'BASE_URL'` | A typo in `config.py`, or the names differ in case | Constants are upper case: `BASE_URL`, `API_KEY`, `MODEL` |
| The printed URL has `//` or is missing `/v1` | The base URL setting ends with a slash, or lacks `/v1` | Use `http://localhost:11434/v1` with no trailing slash |
| `can't open file '01_raw_http_call.py'` | Wrong folder, or the file name differs from the one typed | `cd` into the project folder and check the file name, including the leading `01_` |

Next: **Step 5 — Sending and Reading the Response**.
