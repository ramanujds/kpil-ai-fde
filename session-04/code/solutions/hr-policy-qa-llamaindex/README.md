# HR Policy Q&A with LlamaIndex

The same assistant as the hand-built hr-policy-qa app, rebuilt with LlamaIndex. You ask a question, the app finds the most relevant parts of some company policy documents, and the model answers from those parts only.

The documents in `docs/` are synthetic, copied from the hand-built app. "Acme" is a made-up company.

## Prerequisites

1. **uv**, the Python package manager.
2. An OpenAI API key.

## Files

| File | What it does |
|---|---|
| `docs/` | Six policies: HR handbook, leave, laptop, work from home, expense reimbursement, IT security. |
| `ingest.py` | Run once. Loads the documents, cuts them into nodes (one per heading), embeds them, and stores them in a Chroma collection in `.chroma/`. |
| `ask.py` | Run for every question. A chat engine rewrites follow-up questions, retrieves the closest nodes, answers with `gpt-4o-mini`, and prints where the answer came from, with scores. |
| `.env.example` | Template for the key. Copy it to `.env` and paste your key. `.env` is ignored by Git. |

## Run

Copy `.env.example` to `.env` and put your real key in it, then:

```
uv sync
uv run ingest.py
uv run ask.py
```

Run `ingest.py` again only when you change the documents. It rebuilds the collection from scratch each time.

## What Changed From the Hand-Built App

| Step | Hand-built app | This app |
|---|---|---|
| Load | `Path.glob` over `*.md` files | `SimpleDirectoryReader`, which also reads PDF and Word files once the `llama-index-readers-file` package is added |
| Chunk | Split the text on `## ` by hand | `MarkdownNodeParser`, one node per heading |
| Embed and store | Call the embeddings API, then `collection.upsert` | `VectorStoreIndex` over a `ChromaVectorStore` does both |
| Retrieve | `collection.query`, always 4 chunks | A retriever with `similarity_top_k=4` and a similarity cut-off that drops weak matches |
| Prompt | Built by hand in an f-string | Built by the chat engine from your system prompt and the retrieved nodes |
| Memory | None, every question stands alone | The chat engine remembers the conversation |
| Sources | Chunk metadata | `response.source_nodes`, with a score for each |

The six RAG steps are the same. Only who writes the glue code has changed.

## Try It

1. Ask "How many days of sick leave do I get?". Then ask "And does it carry forward?". The chat engine rewrites the second question using the first, so it should answer about sick leave. The hand-built app has no memory and cannot do this.
2. Ask "What is the capital of France?". Read the "Retrieved from" list. If every node scored below the cut-off, the list is empty and the model says it could not find the answer.
3. Look at the scores next to each source. In `ask.py`, change `similarity_cutoff` and watch which questions start or stop finding sources. The right value depends on your documents and embedding model, so tune it against real questions.
4. Type `reset` to clear the conversation, and ask the sick leave follow-up again to see the memory gone.

## Notes

- The embedding model in `ask.py` must match the one in `ingest.py`, or the question vectors will not line up with the stored ones.
- The collection is named `policies_llamaindex`, so this app and the hand-built app can sit side by side without sharing a store.
- LlamaIndex's class names and imports change between versions. If an import fails after an upgrade, check the current LlamaIndex documentation.
