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

# ---------------------------------------------------------------
# 5. Remember: the model has NO memory between calls
# ---------------------------------------------------------------
# Each call is independent. To continue a conversation, add the model's
# answer and the next question to the list, and send the WHOLE list again.
messages.append({"role": "assistant", "content": choice.message.content})
messages.append({"role": "user", "content": "Now give me one real-life example."})

follow_up = client.chat.completions.create(
    model=config.MODEL,
    messages=messages,
    temperature=0.2,
    max_tokens=150,
)
print("\nFollow-up answer:", follow_up.choices[0].message.content)
print("Prompt tokens grew to:", follow_up.usage.prompt_tokens, "because the history was re-sent")
