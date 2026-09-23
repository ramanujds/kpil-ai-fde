# Step 6 — Error Handling

> [Back to index](README.md) · Previous: [Site Status Route](05-site-status-route.md) · Next: [Recap and Exercises](07-recap-and-exercises.md)

## Goal

Replace the raw dict lookup with `.get()` plus an explicit `HTTPException`, so an unknown
`site_id` returns a clear `404` with a message instead of crashing with a `500`.

## Why this matters

A `500 Internal Server Error` tells a caller nothing about what went wrong or how to fix
their request — from the outside it looks identical whether your server crashed, your
database is down, or the caller made a typo. A `404` with a `detail` message is a contract:
"this specific thing you asked for doesn't exist," which a caller (a script, a frontend, or
later in this program, an AI agent calling this as a tool) can actually act on — retry with
a different id, show the user a real message, stop looping. Failing clearly instead of
silently is exactly the discipline Block 4 (LLM APIs) and Day 5 (agent tools) build on top
of.

## 1. Import `HTTPException`

```python
from fastapi import FastAPI, HTTPException
```

## 2. Look up with `.get()` and raise on a miss

```python
@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    site = SITE_STATUS.get(site_id)
    if site is None:
        raise HTTPException(status_code=404, detail=f"No site found with id '{site_id}'")
    return site
```

`.get()` returns `None` instead of raising when the key is missing, which gives you a
chance to handle it before it becomes an unhandled crash.

## Try it

```bash
curl http://127.0.0.1:8000/sites/kpil-01/status
```

```json
{"name":"Ring Road Flyover","status":"on-track"}
```

```bash
curl -i http://127.0.0.1:8000/sites/kpil-99/status
```

```text
HTTP/1.1 404 Not Found
...
{"detail":"No site found with id 'kpil-99'"}
```

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

This matches [../solutions/without-uv/main.py](../solutions/without-uv/main.py) exactly.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Unknown id still returns `500` | Still indexing with `SITE_STATUS[site_id]` instead of `.get()` | Switch to `.get()` and check for `None` |
| `NameError: HTTPException is not defined` | Import line wasn't updated | `from fastapi import FastAPI, HTTPException` |
| `404` response has an empty `detail` | `HTTPException` raised without `detail=` | Always pass a `detail=` message |

Next: **[Step 7 — Recap and Exercises](07-recap-and-exercises.md)**.
