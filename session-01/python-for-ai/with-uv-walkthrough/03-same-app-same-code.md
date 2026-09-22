# Step 3 — Same App, Same Code

> [Back to index](README.md) · Previous: [Project Setup With uv](02-project-setup-with-uv.md) · Next: [Recap and Exercises](04-recap-and-exercises.md)

## Goal

Add `main.py` — copied unchanged from the without-uv version — and run it with
`uv run uvicorn`, then confirm every route behaves identically to before.

## Why this matters

This is the actual payoff of the whole comparison: your application code has zero
dependency on which tool installed its packages. `main.py` doesn't know or care whether
`fastapi` came from a `pip install` into a manually activated venv or a `uv sync` into an
automatically managed one. Dependency management is infrastructure underneath your code,
not a part of it — and that separation is what lets a team switch tools like this without
touching a single route.

## 1. Add `main.py`, unchanged

```python
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Site Status API")

SITE_STATUS = {
    "kpil-01": {"name": "Ring Road Flyover", "status": "on-track"},
    "kpil-02": {"name": "Metro Package 3", "status": "delayed"},
    "kpil-03": {"name": "Bridge Widening", "status": "on-hold"},
}


@app.get("/")
def read_root():
    return {"message": "Site Status API is running"}


@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    site = SITE_STATUS.get(site_id)
    if site is None:
        raise HTTPException(status_code=404, detail=f"No site found with id '{site_id}'")
    return site
```

If you built [the without-uv version](../without-uv-walkthrough/06-error-handling.md),
this is exactly the file you already wrote — for the routes, the dict, and the error
handling, see that walkthrough's Steps 3 through 6; nothing here is new Python.

## 2. Run it with `uv run`

```bash
uv run uvicorn main:app --reload
```

`uv run` finds `.venv` for this project automatically — no `source .venv/bin/activate`
first, unlike Step 3 of the without-uv walkthrough.

## Try it

```bash
curl http://127.0.0.1:8000/
```

```json
{"message":"Site Status API is running"}
```

```bash
curl http://127.0.0.1:8000/sites/kpil-02/status
```

```json
{"name":"Metro Package 3","status":"delayed"}
```

```bash
curl -i http://127.0.0.1:8000/sites/kpil-99/status
```

```text
HTTP/1.1 404 Not Found
...
{"detail":"No site found with id 'kpil-99'"}
```

Identical responses to the without-uv version, from identical code.

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Site Status API")

SITE_STATUS = {
    "kpil-01": {"name": "Ring Road Flyover", "status": "on-track"},
    "kpil-02": {"name": "Metro Package 3", "status": "delayed"},
    "kpil-03": {"name": "Bridge Widening", "status": "on-hold"},
}


@app.get("/")
def read_root():
    return {"message": "Site Status API is running"}


@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    site = SITE_STATUS.get(site_id)
    if site is None:
        raise HTTPException(status_code=404, detail=f"No site found with id '{site_id}'")
    return site
```

</details>

This matches [../solutions/with-uv/main.py](../solutions/with-uv/main.py) exactly.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `uv run uvicorn` says it can't find `uvicorn` | `uv sync` (Step 2) wasn't run first, or `pyproject.toml` doesn't list `uvicorn[standard]` | Re-run `uv sync`, then retry |
| Habit of running `uvicorn main:app --reload` directly | That uses whatever Python is on your system `PATH`, not this project's `.venv` | Always prefix with `uv run` in a `uv`-managed project |
| Responses differ from the without-uv version | `main.py` was retyped instead of copied and drifted | Diff against [../solutions/with-uv/main.py](../solutions/with-uv/main.py) |

Next: **[Step 4 — Recap and Exercises](04-recap-and-exercises.md)**.
