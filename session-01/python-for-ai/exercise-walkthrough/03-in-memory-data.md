# Step 3 — In-Memory Data

> [Back to index](README.md) · Previous: [Step 2 — First Route](02-first-route.md) · Next: [Step 4 — Site Status Route](04-site-status-route.md)

## Goal

Add a small Python dict holding synthetic site data, so the next route has something
real to look up.

## Why this matters

Most routes you write in this program will read from something — a database, a file, an
API. A plain dict is the simplest possible stand-in: it behaves like a lookup table
(key in, value out) without needing any external system, which keeps this exercise
focused on the FastAPI mechanics rather than data storage. It is also worth saying
explicitly: this dict resets every time the server restarts, and every request shares
the same one — real applications need a database exactly because of that second point.

## 1. Add `SITE_STATUS`

In `main.py`, add the dict between the `app = FastAPI(...)` line and the `/` route:

```python
app = FastAPI(title="Kalpataru Site Status API")

# Synthetic, in-memory data only -- never real project data.
SITE_STATUS = {
    "site-a": "On Track",
    "site-b": "Delayed",
    "site-c": "On Track",
}


@app.get("/")
def root():
    return {"message": "Kalpataru Site Status API is running"}
```

## Try it

No new route yet, so nothing to call over HTTP. Confirm the file is still valid Python
and the server is still running without errors — with `--reload` active, saving the file
should print a reload line in the `uvicorn` terminal:

```text
WARNING:  WatchFiles detected changes in 'main.py'. Reloading...
INFO:     Application startup complete.
```

If you see that with no traceback underneath it, you're set.

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI

app = FastAPI(title="Kalpataru Site Status API")

# Synthetic, in-memory data only -- never real project data.
SITE_STATUS = {
    "site-a": "On Track",
    "site-b": "Delayed",
    "site-c": "On Track",
}


@app.get("/")
def root():
    return {"message": "Kalpataru Site Status API is running"}
```

</details>

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `NameError: SITE_STATUS` later on | Dict defined below the route that uses it | Move `SITE_STATUS = {...}` above `@app.get("/")` |
| Reload log shows a traceback | Usually a stray comma or missing colon in the dict | Compare against the checkpoint above, character by character |

Next: **[Step 4 — Site Status Route](04-site-status-route.md)**.
