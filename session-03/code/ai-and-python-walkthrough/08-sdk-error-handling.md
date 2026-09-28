# Step 8 — SDK Error Handling

> Back to index · Previous: The Same Call With the SDK · Next: Conversation History

## Goal

Catch the SDK's named exceptions so each failure gets its own short, actionable message.

## Why this matters

In Step 6 you decided what an error meant by inspecting a status code. The SDK has already
done that work: each kind of failure is its own exception class, so your code reads like a
list of situations rather than a chain of `if status == ...` checks.

Order matters. `openai.APIStatusError` is the parent of the specific classes
`AuthenticationError`, `NotFoundError` and `RateLimitError`. Python uses the **first**
`except` that matches, so the specific ones must come first and the general
`APIStatusError` last, as a safety net for any other status code. Reversed, the general
handler would swallow everything and the helpful messages would never appear.

| Exception | Meaning | What we tell the user |
|---|---|---|
| `APIConnectionError` | Could not reach the server | Is Ollama running? |
| `AuthenticationError` | 401: key rejected | Check `LLM_API_KEY` in `.env` |
| `NotFoundError` | 404: model not found | Pull the model, or fix `LLM_MODEL` |
| `RateLimitError` | 429: too many requests | Wait and try again |
| `APIStatusError` | Any other error status | Show the status code |

## 1. Import `openai` itself

The exception classes live on the `openai` module, so add the plain import above the
`from` import:

```python
import openai
from openai import OpenAI
```

## 2. Wrap the call in `try` and `except`

Replace the bare call with:

```python
try:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=150,  # upper limit on the length of the answer
    )
except openai.APIConnectionError:
    raise SystemExit(f"Could not connect to {config.BASE_URL}. Is Ollama running?")
except openai.AuthenticationError:
    raise SystemExit("The API key was rejected. Check LLM_API_KEY in your .env file.")
except openai.NotFoundError:
    raise SystemExit(f"Model '{config.MODEL}' not found. For Ollama, run: ollama pull {config.MODEL}")
except openai.RateLimitError:
    raise SystemExit("Too many requests. Wait a little and try again.")
except openai.APIStatusError as error:
    raise SystemExit(f"API returned an error: {error.status_code}")
```

Only the code that talks to the network sits inside `try`. The code that reads the response
stays outside, so a bug in your own code is never mistaken for a network problem.

## Try it

The normal run should behave exactly as in Step 7:

```bash
uv run python 02_sdk_call.py
```

Now a model that does not exist (macOS or Linux):

```bash
LLM_MODEL=nope uv run python 02_sdk_call.py
```

```text
Model 'nope' not found. For Ollama, run: ollama pull nope
```

And a server that is not there:

```bash
LLM_BASE_URL=http://localhost:9/v1 uv run python 02_sdk_call.py
```

```text
Could not connect to http://localhost:9/v1. Is Ollama running?
```

Ollama ignores API keys, so the 401 message cannot be triggered locally. With a hosted
provider and a wrong key you would see `The API key was rejected. Check LLM_API_KEY in your
.env file.`

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

import openai
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
try:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=150,  # upper limit on the length of the answer
    )
except openai.APIConnectionError:
    raise SystemExit(f"Could not connect to {config.BASE_URL}. Is Ollama running?")
except openai.AuthenticationError:
    raise SystemExit("The API key was rejected. Check LLM_API_KEY in your .env file.")
except openai.NotFoundError:
    raise SystemExit(f"Model '{config.MODEL}' not found. For Ollama, run: ollama pull {config.MODEL}")
except openai.RateLimitError:
    raise SystemExit("Too many requests. Wait a little and try again.")
except openai.APIStatusError as error:
    raise SystemExit(f"API returned an error: {error.status_code}")

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

The file still stops after reading the first answer. Step 9 adds the follow-up question.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `NameError: name 'openai' is not defined` | Only `from openai import OpenAI` is imported | Add `import openai` |
| The specific messages never appear, only the generic one | `APIStatusError` is listed before the specific classes | Put `APIStatusError` last |
| The 401 message never shows when testing locally | Ollama ignores API keys, so a wrong key is never rejected | Expected. The message appears only with a hosted provider |
| Every failure shows as a connection error | An over-broad `except Exception` above the specific ones | Remove it, or move it below them |

Next: **Step 9 — Conversation History**.
