# Step 4 — In-Memory Data

> Back to index · Previous: First Route · Next: Site Status Route

## Goal

Add a `SITE_STATUS` dictionary holding a few synthetic construction sites, keyed by id, so
the next step has something real to look up.

## Why this matters

A dict keyed by id is the same shape you'll get back from a real database row, a
spreadsheet lookup, or an LLM tool-call result later in the program — a stable identifier
mapped to a small record. Using a plain dict here, in memory, lets you practise that shape
without a database in the way. It's also the same reason dict lookups matter for AI work
specifically: an agent's "tool" is usually a function that takes an id or a query and
returns exactly this kind of small structured record.

## 1. Add the data, above the routes

```python
from fastapi import FastAPI

app = FastAPI(title="Site Status API")

SITE_STATUS = {
    "kpil-01": {"name": "Ring Road Flyover", "status": "on-track"},
    "kpil-02": {"name": "Metro Package 3", "status": "delayed"},
    "kpil-03": {"name": "Bridge Widening", "status": "on-hold"},
}


@app.get("/")
def read_root():
    return {"message": "Site Status API is running"}
```

Every value is itself a small `dict` — the same shape the API will hand back as JSON once
a route reads from this.

## Try it

No route reads `SITE_STATUS` yet, so there's nothing new to `curl`. Confirm the dict is
well-formed instead:

```bash
python3 -c "from main import SITE_STATUS; print(SITE_STATUS['kpil-02'])"
```

Expect:

```text
{'name': 'Metro Package 3', 'status': 'delayed'}
```

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI

app = FastAPI(title="Site Status API")

SITE_STATUS = {
    "kpil-01": {"name": "Ring Road Flyover", "status": "on-track"},
    "kpil-02": {"name": "Metro Package 3", "status": "delayed"},
    "kpil-03": {"name": "Bridge Widening", "status": "on-hold"},
}


@app.get("/")
def read_root():
    return {"message": "Site Status API is running"}
```

</details>

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `SyntaxError` pointing at the dict | Missing comma between entries, or mismatched quotes | Check each `"key": {...},` line ends with a comma |
| `python3 -c` command fails to import `main` | Not running the command from the folder containing `main.py` | `cd` into the project folder first |
| Typo in a key you'll need next step | `kpil-01` vs `kpil_01` vs `KPIL-01` | Keep ids lowercase with hyphens, consistently |

Next: **Step 5 — Site Status Route**.
