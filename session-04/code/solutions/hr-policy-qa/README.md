# HR Policy Q&A (RAG)

The simplest RAG app. You ask a question, the app finds the most relevant parts of some company policy documents, and the model answers from those parts only.

The documents in `docs/` are synthetic. "Acme" is a made-up company.

## Prerequisites

1. **uv**, the Python package manager.
2. An OpenAI API key.

## Files

| File | What it does |
|---|---|
| `docs/` | Six policies: HR handbook, leave, laptop, work from home, expense reimbursement, IT security. |
| `ingest.py` | Run once. Loads the documents, cuts them into chunks (one per section), turns each chunk into a vector, and stores them in a Chroma vector store in `.chroma/`. |
| `ask.py` | Run for every question. Turns the question into a vector, finds the 4 closest chunks, sends them to `gpt-4o-mini` with the question, and prints the answer and where it came from. |
| `.env.example` | Template for the key. Copy it to `.env` and paste your key. `.env` is ignored by Git. |

## Run

Copy `.env.example` to `.env` and put your real key in it, then:

```
uv sync
uv run ingest.py
uv run ask.py
```

Run `ingest.py` again only when you change the documents.

Try it: ask "Can a first-year employee carry forward unused leave?" and read the "Retrieved from" list. Then ask "What is the capital of France?". The model should say it could not find the answer, because nothing in the documents covers it.
