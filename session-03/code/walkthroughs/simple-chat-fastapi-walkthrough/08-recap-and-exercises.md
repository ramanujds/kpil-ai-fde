# Step 8 — Recap and Exercises

> Back to index · Previous: The Chat Page

## Quick Reference

| Concept | Where it lives |
|---|---|
| The app object | `app = FastAPI(...)` in `main.py` |
| Model client and name | `client` and `MODEL` in `main.py` |
| Request schema | `class ChatRequest(BaseModel)` |
| Chat history | `messages`, a module-level list in `main.py` |
| Saving to history | The two `append` calls in `chat`, after the model answers |
| Error handling | `try` / `except OpenAIError` raising `HTTPException(503)` |
| Serving the page | `FileResponse("static/index.html")` in `home` |
| Page to API calls | `fetch` calls to `/chat` and `/history` in `static/index.html` |
| Interactive testing | `/docs` (Swagger) |

## Gotchas

| Gotcha | Why it happens |
|---|---|
| Everyone shares one conversation | There is a single `messages` list for the whole server |
| History disappears on restart or on a code edit | It lives in memory, and `fastapi dev` restarts on save |
| `Not Found` or file error on `/` | The server was started outside the project folder, so `static/index.html` is not found |
| 422 from `/chat` | The body was not JSON with a `message` text field |
| 503 "Could not reach the model" | Ollama is not running or `llama3:8b` is not pulled |
| Replies get slower in a long chat | Every request re-sends the whole history |
| Answers differ on every run | Models choose words with some randomness |

## Discussion Questions

1. Who holds the conversation, the page or the server? How do you know?
2. Why is the user's message saved only after the model answers?
3. What happens if two people open the page at the same time? How would you give each person their own history?
4. Why did the history live in a loop in `simple-chat` but at module level here?
5. What does the 422 in Step 4 protect your code from?
6. Why does the page draw the user's bubble before the server replies, and what is the risk?

## Exercises

1. Change `MODEL` to another model you have pulled and restart the server.
2. Add a `GET /health` endpoint returning `{"status": "ok"}`.
3. Add a `system` message at the start of `messages` that makes the model answer in one sentence. Decide what `DELETE /history` should do with it.
4. Add a `Field(min_length=1)` to `ChatRequest.message` and check what Swagger returns for an empty message.
5. Add `GET /history/count` returning the number of messages.
6. Keep only the last 10 messages when sending to the model, but keep all of them in the history.
7. Rebuild `main.py` and `static/index.html` from memory in an empty folder, then compare with the reference.

## What's Next

The weak points are the ones named in the gotchas: one shared conversation and memory that
vanishes on restart. Natural next steps are one history per user (for example keyed by a
session id sent from the page), saving the history to a file or database, and streaming the
answer word by word instead of waiting for the whole reply.
