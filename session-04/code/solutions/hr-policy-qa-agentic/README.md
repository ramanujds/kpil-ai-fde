# HR Policy Q&A (Agentic RAG)

The agentic version of `hr-policy-qa`. In the simple app, every question goes through one fixed pipeline: embed, fetch 4 chunks, answer. Here the model is given **tools** and decides for itself what to do: search one document, search several, look up who you are, retry with better words, or answer without searching at all.

The documents in `docs/` and the employees in `employees.json` are synthetic. "Acme" is a made-up company.

## Prerequisites

1. **uv**, the Python package manager.
2. An OpenAI API key.

## Files

| File | What it does |
|---|---|
| `docs/` | The same six policies as the simple app. |
| `employees.json` | Four made-up employees (E101 to E104) with role, level and joining date. |
| `ingest.py` | Run once. Identical to the simple app: chunks by section, embeds, stores in Chroma in `.chroma/`. |
| `ask.py` | Run for every question. Gives the model two tools and runs the loop described below. |
| `.env.example` | Template for the key. Copy it to `.env` and paste your key. `.env` is ignored by Git. |

## The Two Tools

| Tool | What it does |
|---|---|
| `search_policies(query, document)` | Finds the 3 closest chunks, optionally inside one document, and returns each with a relevance score. |
| `get_my_profile()` | Returns the signed-in employee's role, level, joining date and months of service. It takes no ID, so the model can never read anyone else's record. |

## The Agent Loop

```
question -> model -> wants a tool? -- yes -> run it, give the result back -> model ...
                          |
                          no -> that is the final answer
```

`ask.py` repeats this until the model answers or `MAX_STEPS` (5) is reached. At the limit, the model is told to stop searching and answer with what it has. Each tool call is printed as `->` so you can watch the decisions being made.

## Run

Copy `.env.example` to `.env` and put your real key in it, then:

```
uv sync
uv run ingest.py
uv run ask.py
```

Sign in with an employee ID (E101 is a one-month-old joiner, E103 is a manager). Run `ingest.py` again only when you change the documents.

## Try It

| Ask as | Question | What to watch |
|---|---|---|
| any | "Hi, thanks!" | No tool call at all. |
| E101 | "What is my notice period?" | `get_my_profile` first, then a search, then the 30-day probation answer. |
| E103 | "What is my notice period?" | Same question, a different answer (90 days), because the profile differs. |
| any | "Compare the leave policy and the work from home policy on manager approval." | Two searches, one per document, then one combined answer. |
| E101 | "Can I carry forward unused leave?" then "And can I work from home?" | The second question works because the history is kept between questions. |
| any | "What is the capital of France?" | The model should say it could not find it, and not answer from memory. |

## Compared With the Simple App

| | `hr-policy-qa` | `hr-policy-qa-agentic` |
|---|---|---|
| Searches per question | Always 1 | 0, 1 or several |
| Chooses the document | No | Yes |
| Knows who is asking | No | Yes, through `get_my_profile` |
| Retries a weak result | No | Yes, if the model judges the relevance score too low |
| Model calls per question | 1 | 1 to 6 |
| Speed and cost | Lower | Higher |
| Same question twice | Same steps | Steps may differ |

## Things to Know

- **It is not guaranteed.** The model decides which tools to call, and `gpt-4o-mini` sometimes skips `get_my_profile` and answers with "if you are still on probation...". Ask the same question twice and compare. This is the unpredictability the notes describe.
- **Cost.** Every step is another model call. On a free tier you reach the rate limit sooner than with the simple app.
- **Errors are handled in two places.** A bad tool call (unknown tool, malformed arguments) goes back to the model as text so it can recover. A failed model call (rate limit, bad key, no network) prints a message, drops that half-finished turn and lets you ask again.
- **Access.** Tools are the doors. Here the only record door is scoped to the signed-in user. In a real system, apply the same rule to every tool.
- **No framework.** The loop is about 20 lines of plain Python. Agent frameworks, taught on Day 5, wrap this same pattern.
