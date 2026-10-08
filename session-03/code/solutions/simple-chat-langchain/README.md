# Simple Chat with LangChain

The `simple-chat` project rebuilt with LangChain. Same app, same behaviour, so you can see exactly what LangChain changes. Every line that differs from `simple-chat` is marked with a `CHANGED` comment in the code.

## Prerequisites

1. **uv**, the Python package manager.
2. **Ollama** running, with the model downloaded once: `ollama pull llama3:8b`.
3. For `chat_openai.py` only: an OpenAI key. Copy `.env.example` to `.env` and paste the key in. `.env` is ignored by Git.

## Files

| File | What it does | Matches in `simple-chat` |
|---|---|---|
| `chat.py` | Basic chat with `llama3:8b`, no memory | `chat.py` and `chat_ollama.py` |
| `chat_with_history.py` | Same, with a `messages` list so the model remembers | `chat_with_history.py` |
| `chat_openai.py` | Basic chat with OpenAI's `gpt-4o-mini` | `chat_openai.py` |

## Run

```
uv sync
uv run chat.py
uv run chat_with_history.py
uv run chat_openai.py
```

## What Changed

| Area | Plain SDK (`simple-chat`) | LangChain (this project) |
|---|---|---|
| Packages | `openai`, `ollama`, `python-dotenv` | `langchain-ollama`, `langchain-openai`, `python-dotenv` |
| Create the model | `OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")` | `ChatOllama(model="llama3:8b")` |
| Send a question | `client.chat.completions.create(model=..., messages=[{"role": "user", "content": ...}])` | `model.invoke(user_input)` |
| Read the answer | `response.choices[0].message.content` (OpenAI SDK) or `response.message.content` (Ollama library) | `response.content`, for every provider |
| User message in history | `{"role": "user", "content": user_input}` | `HumanMessage(user_input)` |
| Model answer in history | `{"role": "assistant", "content": answer}` | `AIMessage(response.content)` |
| Switch to OpenAI | A different client, no `base_url`, and a new way to set the key | Change one line: `ChatOpenAI(model="gpt-4o-mini")` |

## What Did Not Change

- The `while True` loop, the quit check and the `input()` call.
- The idea of memory: a list that grows, sent in full every turn.
- The need for Ollama running locally, or a key for OpenAI.

## The Main Point

In `simple-chat`, the three provider files read the answer in two different ways. Here, `chat.py` and `chat_openai.py` have the same loop and read the answer the same way. Only the line that creates the model differs. That is the one thing LangChain buys you in this small app, and it grows more valuable as an app gets bigger.

## Honest Trade-Off

For an app this small, the plain SDK is just as easy to read and has fewer packages (`uv sync` here installs many more). LangChain starts to pay off when you add things like switching providers, structured output, tools or RAG.
