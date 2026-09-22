# Step 2 — First Route

> [Back to index](README.md) · Previous: [Step 1 — Environment Setup](01-environment-setup.md) · Next: [Step 3 — In-Memory Data](03-in-memory-data.md)

## Goal

Create the FastAPI app instance and a single route, `GET /`, and see it respond over
HTTP.

## Why this matters

FastAPI turns an ordinary Python function into a web endpoint using a decorator
(`@app.get(...)`). There is no separate routing file, no manual request parsing — you
write a function, you tell FastAPI which URL and method it answers, and returning a
dict is enough to produce a JSON response. Seeing that round trip work for the simplest
possible route, before adding any real logic, is what makes the rest of the build feel
mechanical rather than mysterious.

## 1. Create `main.py`

In **both** project folders (`site-status-without-uv/` and `site-status-with-uv/`),
create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="Kalpataru Site Status API")


@app.get("/")
def root():
    return {"message": "Kalpataru Site Status API is running"}
```

`app = FastAPI(...)` creates the application object every route attaches to. The
`title` shows up on the `/docs` page you'll open below.

## Try it

Start the server. Without-uv (venv still active):

```bash
uvicorn main:app --reload
```

With uv:

```bash
uv run uvicorn main:app --reload
```

Both print something like:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

Now, from a second terminal (or a browser):

```bash
curl http://127.0.0.1:8000/
```

```json
{"message":"Kalpataru Site Status API is running"}
```

Open `http://127.0.0.1:8000/docs` in a browser — FastAPI's interactive test page,
generated from the one route you just wrote, with nothing extra to build.

Leave the server running; `--reload` picks up your changes in the next steps
automatically.

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI

app = FastAPI(title="Kalpataru Site Status API")


@app.get("/")
def root():
    return {"message": "Kalpataru Site Status API is running"}
```

</details>

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `uvicorn: command not found` | Not using the project's own environment | Confirm `.venv` is active (without-uv), or prefix with `uv run` (with-uv) |
| `Address already in use` | A previous server is still running on port 8000 | Stop it with `Ctrl+C` in its terminal, or add `--port 8001` |
| `curl` hangs or connection refused | Server not started yet, or wrong port | Check the terminal running `uvicorn` for its actual URL |

Next: **[Step 3 — In-Memory Data](03-in-memory-data.md)**.
