# Step 5 — Error Handling

> [Back to index](README.md) · Previous: [Step 4 — Site Status Route](04-site-status-route.md) · Next: [Step 6 — Recap and Exercises](06-recap-and-exercises.md)

## Goal

Replace the crash from Step 4 with a clear, structured 404 response when a site is
unknown.

## Why this matters

A `KeyError` traceback and a `500 Internal Server Error` tell the caller nothing useful
— and in a real deployment, a raw traceback can leak internal details you did not mean
to expose. `HTTPException` is FastAPI's built-in way to say, deliberately, "this request
is invalid, here is why, and here is the status code that means that." This is the same
shape of decision you will make constantly from Day 3 onward: an LLM API call can fail,
a document lookup can come up empty, a tool call can get bad input — in every case, the
fix is the same pattern, not a crash.

## 1. Switch from indexing to `.get()`, and check the result

```python
from fastapi import FastAPI, HTTPException
```

```python
@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    status = SITE_STATUS.get(site_id.lower())
    if status is None:
        raise HTTPException(status_code=404, detail=f"Unknown site '{site_id}'")
    return {"site_id": site_id, "status": status}
```

`dict.get(key)` returns `None` instead of raising when the key is missing, which is what
lets you check for the missing case yourself and decide what to do about it, instead of
FastAPI deciding for you (a 500).

## Try it

Restart is automatic under `--reload`. Request the same unknown site as in Step 4:

```bash
curl -i http://127.0.0.1:8000/sites/site-x/status
```

```text
HTTP/1.1 404 Not Found
...
{"detail":"Unknown site 'site-x'"}
```

Confirm known sites still work:

```bash
curl http://127.0.0.1:8000/sites/site-c/status
```

```json
{"site_id":"site-c","status":"On Track"}
```

The `uvicorn` terminal should now show a clean `404` log line instead of a traceback.

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI, HTTPException

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


@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    status = SITE_STATUS.get(site_id.lower())
    if status is None:
        raise HTTPException(status_code=404, detail=f"Unknown site '{site_id}'")
    return {"site_id": site_id, "status": status}
```

</details>

This matches [../exercise/without-uv/main.py](../exercise/without-uv/main.py) and
[../exercise/with-uv/main.py](../exercise/with-uv/main.py) exactly.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Still get a 500 on unknown sites | Left `SITE_STATUS[...]` indexing instead of `.get(...)` | Recheck the lookup line against the checkpoint above |
| `NameError: HTTPException` | Import not updated | `from fastapi import FastAPI, HTTPException` — both names on one line |
| 404 fires even for known sites | `site_id.lower()` typo, or a `SITE_STATUS` key changed by accident | Compare keys against Step 3's checkpoint |

Next: **[Step 6 — Recap and Exercises](06-recap-and-exercises.md)**.
