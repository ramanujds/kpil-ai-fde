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
