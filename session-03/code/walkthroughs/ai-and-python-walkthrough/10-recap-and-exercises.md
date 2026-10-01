# Step 10 — Recap and Exercises

> Back to index · Previous: Conversation History

## Quick reference

| Concept | Where it lives |
|---|---|
| API address, key and model from the environment | `config.py`, `BASE_URL`, `API_KEY`, `MODEL` |
| Settings template that is safe to commit | `.env.example` |
| Real settings and secrets, never committed | `.env`, listed in `.gitignore` |
| Request URL, headers and JSON body | `01_raw_http_call.py`, `url`, `headers`, `payload` |
| Sending a request and reading JSON back | `httpx.post(...)` and `response.json()` |
| The answer inside the reply | `data["choices"][0]["message"]["content"]` |
| Why generation stopped | `finish_reason`: `stop` or `length` |
| Token counts | `usage` in the raw JSON, `response.usage` in the SDK |
| Failures from a raw call | `raise_for_status()`, `httpx.ConnectError`, `httpx.HTTPStatusError` |
| A reusable client object | `02_sdk_call.py`, `client = OpenAI(...)` |
| Roles | `system`, `user`, `assistant` in the `messages` list |
| Failures from the SDK | `openai.APIConnectionError`, `NotFoundError`, and the rest |
| Conversation memory | The `messages` list in your code, re-sent on every call |

## Gotchas

| Gotcha | Why it happens | Fix |
|---|---|---|
| `Could not connect ... Is Ollama running?` | The Ollama app or service is not running | Start the Ollama app, or run `ollama serve` |
| `Server said 404` or `Model ... not found` | The model name is wrong or was never downloaded | Run `ollama pull llama3:8b`, or fix `LLM_MODEL` |
| A 404 with the plain text `page not found` | `LLM_BASE_URL` is missing the `/v1` part | Use `http://localhost:11434/v1` |
| The first answer takes very long | A local model is loading into memory | Wait; later calls are fast |
| Edits to `.env` seem ignored | A variable with the same name is already set in the terminal, and it wins over the file | Unset the terminal variable, or use one source only |
| `ModuleNotFoundError` for `openai`, `httpx` or `dotenv` | Ran plain `python` outside the environment | Use `uv run python ...` from the project folder |
| An answer stops mid-sentence | `finish_reason` is `length`: the token limit was reached | Raise `max_tokens`, or ask for a shorter answer |
| 401 with a hosted provider | Wrong, missing or expired key | Check `LLM_API_KEY`, and never paste a key into a `.py` file |

## Discussion questions

1. The base URL, key and model are read from environment variables instead of being typed
   into the code. Name two problems that would appear if they were hard-coded.
2. Steps 4 to 6 built the request by hand and Step 7 used an SDK. What did the SDK save you
   from writing? What did doing it by hand let you understand?
3. The model has no memory. Where does a chat's "memory" actually live, and what happens to
   the cost of each turn as the chat gets longer?
4. Why does `except openai.APIStatusError` have to come after `except openai.NotFoundError`?
5. `finish_reason` was `length` for a truncated answer. What could go wrong if an application
   ignored that field?

## Exercises

1. In `01_raw_http_call.py`, change the prompt to ask for a short poem. Run it three times
   and compare the token counts.
2. In `02_sdk_call.py`, set `max_tokens=20`. Run it and check that `finish_reason` becomes
   `length`. Then restore `150`.
3. Add a `system` message to the raw request in `01_raw_http_call.py` so it matches the SDK
   version. Compare how the answers differ in tone.
4. Set `temperature` to 0 and run the SDK script three times, then to 1.5 and run three
   more. Which setting gives repeatable answers?
5. Wrap the follow-up call in `02_sdk_call.py` in the same `try` and `except` chain as the
   first call, without copying the whole block twice. Hint: move the call into a small
   function that takes `messages` and returns the response.
6. Turn the follow-up into a loop that asks three questions in a row, printing
   `prompt_tokens` after each. Watch the number climb.
7. Rebuild `01_raw_http_call.py` from a blank file without looking, then compare it to the
   reference file with a diff tool, and explain each difference.

## What's next

The scripts you built call the model once and stop when something goes wrong. The next
pieces of Day 3 turn them into an application:

- A **reusable client** with retries and backoff for rate limits (Lab 2).
- **Structured outputs**, asking the model for JSON and validating it with Pydantic (Lab 3).
- **Function calling**, letting the model ask your code to run a function (Lab 4).
- The **LLM-powered utility app** that combines all three (Lab 5).
