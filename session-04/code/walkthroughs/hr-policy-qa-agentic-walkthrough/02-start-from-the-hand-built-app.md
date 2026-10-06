# Step 2 — Start From the Hand-Built App

> Back to index · Previous: Concepts Overview · Next: The Search Tool

## Goal

Copy the finished hand-built app, give the copy its own name, add the employee data, and
rebuild the vector store so that the new folder is complete before any agent code exists.

## Why this matters

The hand-built walkthrough already covered the project folder, the documents, the key,
`.gitignore`, and the whole ingestion script. Repeating them would teach nothing new, and
nothing about ingestion changes here. Agentic RAG is a change to how you **ask**, not to
how you **prepare**. So this walkthrough starts from a copy of that app and touches only
`ask.py`.

It is a copy and not an edit in place, on purpose. The original stays untouched, so in
Steps 6 and 7 you can run both apps side by side and see exactly what the model is now
deciding for itself.

The vector store is rebuilt in the new folder instead of copied, so the new app owns its
store and a later change to one app cannot spoil the other.

## 1. Copy the App

Run this from the folder that holds your finished `hr-policy-qa`:

```bash
cp -R hr-policy-qa hr-policy-qa-agentic
cd hr-policy-qa-agentic
rm -rf .venv .chroma uv.lock vectors.json ask.py
```

| Removed | Why |
|---|---|
| `.venv` | It points at the original folder and must be rebuilt for the new one |
| `.chroma` | It is the original app's vector store. The new app builds its own |
| `uv.lock` | It pins the old project name. `uv sync` writes a new one |
| `vectors.json` | Left over from an earlier version of the app. It may not exist in yours |
| `ask.py` | You write a new one from scratch in the next steps. The original stays in `hr-policy-qa` for comparison |

Everything else comes along: `docs/`, `.gitignore`, `.env.example`, your `.env` with the
key in it, and `ingest.py`. Do not edit `ingest.py`.

## 2. Change `pyproject.toml`

Replace the contents with:

```toml
[project]
name = "hr-policy-qa-agentic"
version = "0.1.0"
description = "An agentic RAG assistant that decides which tools to use over synthetic company policy documents"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.0.0",
    "openai>=1.50.0",
    "python-dotenv>=1.0.0",
]
```

Only the name and description changed. There are no new packages: the OpenAI library
already supports tools, and the tools themselves are plain Python.

## 3. Add the Employee Data

Create `employees.json`:

```json
{
  "E101": {"name": "Priya Nair", "role": "Software Engineer", "level": "Employee", "department": "Engineering", "joined": "2026-08-10"},
  "E102": {"name": "Rahul Mehta", "role": "Business Analyst", "level": "Employee", "department": "Finance", "joined": "2024-02-05"},
  "E103": {"name": "Meera Iyer", "role": "Engineering Manager", "level": "Manager", "department": "Engineering", "joined": "2021-06-01"},
  "E104": {"name": "Arjun Shah", "role": "UX Designer", "level": "Employee", "department": "Design", "joined": "2026-03-02"}
}
```

These people are made up. They exist so the assistant can answer questions that depend on
who is asking. Look at how the policies are written: the notice period depends on whether
you are on probation or a manager, leave carry-forward depends on being in your first year,
and work from home depends on having finished probation. The file holds the facts about the
person, and the policies hold the rules. The model has to combine the two, and you do not
put any policy logic in the code.

| Person | Why they are in the file |
|---|---|
| E101 Priya | About one month in, so on probation and in her first year |
| E102 Rahul | Over two years in, a confirmed employee |
| E103 Meera | A manager, so a different notice period |
| E104 Arjun | Joined in March 2026: past the 6-month probation, but still in the first year of service |

## 4. Build the Environment and the Store

```bash
uv sync
uv run ingest.py
```

## Try it

```text
Made 40 chunks from the documents.
Stored 40 chunks. Now run ask.py.
```

If the numbers are the same as in the hand-built app, the copy is healthy. There is no
`ask.py` yet, so there is nothing else to run.

## Checkpoint

<details>
<summary>Full <code>pyproject.toml</code></summary>

```toml
[project]
name = "hr-policy-qa-agentic"
version = "0.1.0"
description = "An agentic RAG assistant that decides which tools to use over synthetic company policy documents"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.0.0",
    "openai>=1.50.0",
    "python-dotenv>=1.0.0",
]
```

</details>

<details>
<summary>Full <code>employees.json</code></summary>

```json
{
  "E101": {"name": "Priya Nair", "role": "Software Engineer", "level": "Employee", "department": "Engineering", "joined": "2026-08-10"},
  "E102": {"name": "Rahul Mehta", "role": "Business Analyst", "level": "Employee", "department": "Finance", "joined": "2024-02-05"},
  "E103": {"name": "Meera Iyer", "role": "Engineering Manager", "level": "Manager", "department": "Engineering", "joined": "2021-06-01"},
  "E104": {"name": "Arjun Shah", "role": "UX Designer", "level": "Employee", "department": "Design", "joined": "2026-03-02"}
}
```

</details>

These match the reference project's `pyproject.toml` and `employees.json` exactly. The
`.gitignore`, `.env.example`, `docs/` and `ingest.py` need no change. Your `uv.lock` is
created by `uv sync`, and its contents may differ slightly. Your `.env` holds your own key
and is not compared with anything.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `cp: hr-policy-qa: No such file or directory` | You ran the command from the wrong folder | `cd` to the folder that contains `hr-policy-qa`, then run it again |
| `uv run ingest.py` fails with an authentication error | `.env` was not copied, for example because the original lives elsewhere | Run `cp .env.example .env` and paste your key, as in the hand-built walkthrough |
| `json.decoder.JSONDecodeError` later, when `ask.py` starts | A comma or brace is missing in `employees.json` | Compare it with the checkpoint. JSON allows no trailing comma after the last entry |
| `ingest.py` reports a different count from the hand-built app | The `docs/` folder was changed or only partly copied | Copy `docs/` again from `hr-policy-qa` |

Next: **Step 3 — The Search Tool**.
