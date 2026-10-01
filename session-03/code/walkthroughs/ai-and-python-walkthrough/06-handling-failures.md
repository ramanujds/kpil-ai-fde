# Step 6 — Handling Failures

> Back to index · Previous: Sending and Reading the Response · Next: The Same Call With the SDK

## Goal

Wrap the call so a stopped server and a bad model name produce one clear sentence instead of
a stack trace, and so error responses never reach the code that reads `choices`.

## Why this matters

A call to an LLM crosses a network to another program, so failures are normal, not rare:
the server is not running, the URL is wrong, the model name is misspelled, the key is
rejected, or the provider says "slow down". Without handling, the trainee sees a long
traceback and has to guess which of these it was.

There is also a subtler trap. When a server rejects a request, it still replies with valid
JSON, an error message, and your code carries on and fails later with `KeyError: 'choices'`,
far from the real cause. `raise_for_status()` closes that gap: any 4xx or 5xx reply becomes an
exception **at the point of the call**, where the cause is obvious.

The status codes worth recognising:

| Code | Meaning | Usual cause here |
|---|---|---|
| 401 | Unauthorized | Wrong or missing API key on a hosted provider |
| 404 | Not found | Wrong model name, or a base URL missing `/v1` |
| 429 | Too many requests | Rate limit hit. Wait, then retry |
| 5xx | Server error | Provider problem. Retry later |

This step only reports errors clearly. Automatic retries with backoff come with the reusable
client later in Day 3.

## 1. Turn error statuses into exceptions

Right after the call, add `raise_for_status()`:

```python
    response.raise_for_status()  # turns 4xx/5xx status codes into an exception
```

## 2. Wrap the call in `try` and `except`

Replace the bare call with this block:

```python
# ---------------------------------------------------------------
# 4. Make the call
# ---------------------------------------------------------------
# A local model can take a while on its first answer, so allow 120 seconds.
try:
    response = httpx.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()  # turns 4xx/5xx status codes into an exception
except httpx.ConnectError:
    raise SystemExit(f"Could not connect to {config.BASE_URL}. Is Ollama running?")
except httpx.HTTPStatusError as error:
    # 401 = bad key, 404 = model not found, 429 = rate limited, 5xx = server problem
    raise SystemExit(f"Server said {error.response.status_code}: {error.response.text}")
```

Two different failures, two different messages:

| Exception | When it happens | What we say |
|---|---|---|
| `httpx.ConnectError` | Nothing is listening at the address | Could not connect. Is Ollama running? |
| `httpx.HTTPStatusError` | The server replied with a 4xx or 5xx | The status code and the server's own explanation |

`raise SystemExit("message")` prints the message and stops the program with a failure exit
code, with no traceback. That is the right behaviour for a small script; a larger program
would log the error and decide whether to retry.

## Try it

First the normal run still works:

```bash
uv run python 01_raw_http_call.py
```

Now break it on purpose. Point at a port with nothing behind it (macOS or Linux):

```bash
LLM_BASE_URL=http://localhost:9/v1 uv run python 01_raw_http_call.py
```

The last line of output:

```text
Could not connect to http://localhost:9/v1. Is Ollama running?
```

Ask for a model that does not exist:

```bash
LLM_MODEL=nope uv run python 01_raw_http_call.py
```

```text
Server said 404: {"error":{"message":"model 'nope' not found","type":"not_found_error","param":null,"code":null}}
```

On Windows PowerShell, set the variable first, for example `$env:LLM_MODEL="nope"`, run the
script, then clear it with `Remove-Item Env:LLM_MODEL`.

## Checkpoint

<details>
<summary>Full <code>01_raw_http_call.py</code></summary>

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

import httpx

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

# ---------------------------------------------------------------
# 4. Make the call
# ---------------------------------------------------------------
# A local model can take a while on its first answer, so allow 120 seconds.
try:
    response = httpx.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()  # turns 4xx/5xx status codes into an exception
except httpx.ConnectError:
    raise SystemExit(f"Could not connect to {config.BASE_URL}. Is Ollama running?")
except httpx.HTTPStatusError as error:
    # 401 = bad key, 404 = model not found, 429 = rate limited, 5xx = server problem
    raise SystemExit(f"Server said {error.response.status_code}: {error.response.text}")

# ---------------------------------------------------------------
# 5. Read the response
# ---------------------------------------------------------------
data = response.json()  # JSON text -> Python dict

print("\nStatus code:", response.status_code)
print("Full response:")
print(json.dumps(data, indent=2))

# The answer sits inside: choices -> first choice -> message -> content
answer = data["choices"][0]["message"]["content"]
print("\nAnswer:", answer)

# Why did the model stop? "stop" means it finished naturally.
# "length" would mean it ran out of room (max tokens).
print("Finish reason:", data["choices"][0]["finish_reason"])

# usage tells you how much text was processed. Tokens are what cloud APIs bill for.
usage = data.get("usage", {})
print("Tokens used:", usage)
```

</details>

This matches the reference project's `01_raw_http_call.py` exactly.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Still a `KeyError: 'choices'` on a bad model | `raise_for_status()` is missing, or sits outside the `try` block | Put it on the line right after `httpx.post(...)`, inside `try` |
| Long traceback instead of the friendly message | Catching the wrong exception class | Use `httpx.ConnectError` and `httpx.HTTPStatusError` |
| `NameError: name 'error' is not defined` | The `as error` part is missing from the status handler | `except httpx.HTTPStatusError as error:` |
| The 404 says `page not found` instead of a JSON error | The base URL is missing `/v1` | Set `LLM_BASE_URL` to end with `/v1` |

Next: **Step 7 — The Same Call With the SDK**.
