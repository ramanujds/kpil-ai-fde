# Step 3 — First Route

> [Back to index](README.md) · Previous: [Environment Setup](02-environment-setup.md) · Next: [In-Memory Data](04-in-memory-data.md)

## Goal

Create `main.py` with a FastAPI app and a single `GET /` route, and confirm the whole
chain — code, server, request, response — works before adding any real logic.

## Why this matters

The biggest source of confusion in a first API exercise isn't the logic, it's the
plumbing: is the server even running, is it on the port you think, did the file save. Prove
the simplest possible version works end to end first, so any problem you hit later is
about the code you just added, not about a broken setup you carried forward unnoticed.

## 1. Create the app and the first route

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="Site Status API")


@app.get("/")
def read_root():
    return {"message": "Site Status API is running"}
```

`app` is the FastAPI application object. `@app.get("/")` registers the function right
below it to handle `GET` requests to `/`. Returning a `dict` is enough — FastAPI converts
it to a JSON response automatically.

## Try it

```bash
uvicorn main:app --reload
```

In another terminal:

```bash
curl http://127.0.0.1:8000/
```

Expect:

```json
{"message":"Site Status API is running"}
```

You can also open `http://127.0.0.1:8000/docs` in a browser for FastAPI's interactive,
auto-generated test page — no extra code required for that.

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI

app = FastAPI(title="Site Status API")


@app.get("/")
def read_root():
    return {"message": "Site Status API is running"}
```

</details>

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `command not found: uvicorn` | Venv not activated in this terminal | Re-activate: `source .venv/bin/activate` |
| Running `python main.py` does nothing | `main.py` defines the app but never starts a server itself | Always run it via `uvicorn main:app --reload`, not directly |
| `address already in use` | A previous `uvicorn` process from an earlier attempt is still running | Stop it (`Ctrl+C` in its terminal), or run with `--port 8001` |

Next: **[Step 4 — In-Memory Data](04-in-memory-data.md)**.
