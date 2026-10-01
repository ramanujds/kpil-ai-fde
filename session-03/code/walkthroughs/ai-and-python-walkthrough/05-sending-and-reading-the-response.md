# Step 5 — Sending and Reading the Response

> Back to index · Previous: Building the Request · Next: Handling Failures

## Goal

Send the request with `httpx`, print the full JSON reply, and pull out the three things you
usually want: the answer, why the model stopped, and the token counts.

## Why this matters

The response is a nested structure, and the answer is buried in it: the list `choices`, its
first item, then `message`, then `content`. Nothing about a chat model returns "just the
text". Alongside the text you get two pieces of information that matter a lot in real
applications:

- **Finish reason.** `stop` means the model finished. `length` means it ran out of room and
  the answer is cut off. Ignoring this is how truncated answers slip into production.
- **Usage.** Prompt tokens, completion tokens and a total. Hosted providers bill by the
  token, and every model has a limit on how many it can handle, so this is where cost and
  limits become visible.

Printing the **full** response first, before extracting anything, teaches you where the
fields are, so extracting them later is not guesswork.

## 1. Import `httpx`

Add it above `import config`, with a blank line between the two groups:

```python
import json

import httpx

import config
```

## 2. Send the request

Below the request printing, add a new section:

```python
# ---------------------------------------------------------------
# 4. Make the call
# ---------------------------------------------------------------
# A local model can take a while on its first answer, so allow 120 seconds.
response = httpx.post(url, headers=headers, json=payload, timeout=120)
```

`json=payload` makes `httpx` convert the dict to JSON text and set the content type for you.
`timeout=120` allows two minutes, because a local model can be slow to answer the first time
while it loads into memory.

## 3. Read the JSON reply

```python
# ---------------------------------------------------------------
# 5. Read the response
# ---------------------------------------------------------------
data = response.json()  # JSON text -> Python dict
```

`response.json()` turns the JSON text back into a Python dict, the reverse of what
`json.dumps` did on the way out.

## 4. Print the status and the full response

```python
print("\nStatus code:", response.status_code)
print("Full response:")
print(json.dumps(data, indent=2))
```

## 5. Extract the answer

```python
# The answer sits inside: choices -> first choice -> message -> content
answer = data["choices"][0]["message"]["content"]
print("\nAnswer:", answer)
```

## 6. Check why it stopped

```python
# Why did the model stop? "stop" means it finished naturally.
# "length" would mean it ran out of room (max tokens).
print("Finish reason:", data["choices"][0]["finish_reason"])
```

## 7. Check the token usage

```python
# usage tells you how much text was processed. Tokens are what cloud APIs bill for.
usage = data.get("usage", {})
print("Tokens used:", usage)
```

`.get("usage", {})` returns an empty dict instead of crashing if a provider leaves the field
out.

## Try it

Make sure Ollama is running, then:

```bash
uv run python 01_raw_http_call.py
```

After the request body from Step 4, you should see something like this. The wording of the
answer and the `id` and `created` values will differ on your machine:

```text
Status code: 200
Full response:
{
  "id": "chatcmpl-531",
  "object": "chat.completion",
  "created": 1790199676,
  "model": "llama3:8b",
  "system_fingerprint": "fp_ollama",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "An API, or Application Programming Interface, is a set of defined rules ..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 21,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "completion_tokens": 58,
    "total_tokens": 79
  }
}

Answer: An API, or Application Programming Interface, is a set of defined rules ...
Finish reason: stop
Tokens used: {'prompt_tokens': 21, 'prompt_tokens_details': {'cached_tokens': 0}, 'completion_tokens': 58, 'total_tokens': 79}
```

Find the answer inside the full JSON, then find the same text on the `Answer:` line.

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
response = httpx.post(url, headers=headers, json=payload, timeout=120)

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

The file is still missing error handling, which comes in Step 6.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `httpx.ConnectError` with a long stack trace | Ollama is not running | Start Ollama. Step 6 turns this into a short message |
| `KeyError: 'choices'` | The server replied with an error body, for example an unknown model, and there is no `choices` field | Print `response.text` to read the error. Step 6 handles this properly |
| `httpx.ReadTimeout` on the first run | The model is still loading into memory | Wait and rerun; later calls are much faster |
| `KeyError: 'content'` or an empty answer | Indexing the wrong level of the JSON | Follow the path exactly: `choices`, index 0, `message`, `content` |

Next: **Step 6 — Handling Failures**.
