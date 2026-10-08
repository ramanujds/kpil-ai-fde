# Simple Chat

The most basic chat app. You type a question, the model answers. There is no memory, so each question is treated as a brand new conversation.

## Prerequisites

1. **uv**, the Python package manager.
2. **Ollama** running, with the model downloaded once: `ollama pull llama3:8b`.

## Files

| File | What it does |
|---|---|
| `chat.py` | Calls Ollama through the OpenAI SDK. The same code would work with OpenAI by changing the URL, key and model. |
| `chat_ollama.py` | Calls Ollama through its own `ollama` library. Same behaviour, a slightly shorter setup. |
| `chat_openai.py` | Calls OpenAI's `gpt-4o-mini` with your own API key. Needs a `.env` file (see below). |
| `chat_with_history.py` | Same as `chat.py`, but keeps a `messages` list and sends the whole conversation every turn, so the model remembers earlier questions. |
| `.env.example` | Template for the key. Copy it to `.env` and paste your key. `.env` is ignored by Git. |

## Run

```
uv sync
uv run chat.py
uv run chat_ollama.py
```

For the OpenAI version, first copy `.env.example` to `.env`, put your real key in it, then:

```
uv run chat_openai.py
```

Try it: say "My name is Asha", then ask "What is my name?". The three files above will not know, because nothing from the first message is sent with the second.

Now run the history version and ask the same two questions:

```
uv run chat_with_history.py
```

This time the model answers "Asha", because the first question and answer are sent along with the second.
