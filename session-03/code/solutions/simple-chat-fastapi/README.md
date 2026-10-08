# Simple Chat with FastAPI

The `simple-chat` app with chat history, turned into a web service with a one-page UI. You type in the browser, the page calls the API, the API calls `llama3:8b` through Ollama, and the page shows the whole conversation.

## Prerequisites

1. **uv**, the Python package manager.
2. **Ollama** running, with the model downloaded once: `ollama pull llama3:8b`.

## Run

```
uv sync
uv run fastapi dev
```

Open http://127.0.0.1:8000 for the chat. Swagger is at http://127.0.0.1:8000/docs.

## Files

| File | What it does |
|---|---|
| `main.py` | The API: serves the page, handles `/chat`, keeps the history |
| `static/index.html` | The chat page: input box, conversation view and a New chat button. Plain HTML and JavaScript, no build step. |
| `pyproject.toml` and `uv.lock` | Dependencies (`fastapi[standard]`, `openai`) |

## Endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/` | The chat page |
| POST | `/chat` | Body `{"message": "..."}`. Returns `{"answer": "..."}` and saves both to the history. |
| GET | `/history` | The complete conversation as a list of messages |
| DELETE | `/history` | Clears the history for a new chat |

## What Changed From simple-chat

| Area | simple-chat | This project |
|---|---|---|
| Input and output | `input()` and `print()` in a terminal | A browser page calling `POST /chat` |
| The loop | `while True` | The browser sends one request per message; the server handles each one |
| History | A `messages` list in the loop | The same list, at module level in `main.py`, so it lives as long as the server runs |
| Showing the conversation | Scrolls past in the terminal | `GET /history` feeds the page, so a refresh brings it back |
| Errors | The program crashes | A 503 with a message, shown under the chat box |

## Things to Know

- There is **one shared conversation** for everyone who opens the page. That is fine for learning, but a real app keeps one history per user.
- The history lives in memory, so restarting the server clears it.
- If Ollama is not running, the page shows "Could not reach the model" and the failed question is not saved.
