# Step 4 — Site Status Route

> [Back to index](README.md) · Previous: [Step 3 — In-Memory Data](03-in-memory-data.md) · Next: [Step 5 — Error Handling](05-error-handling.md)

## Goal

Add the second route, `GET /sites/{site_id}/status`, that reads `site_id` out of the URL
and looks it up in `SITE_STATUS` — for known sites only, for now.

## Why this matters

`{site_id}` in the route path is a **path parameter**: FastAPI matches that segment of
the URL, passes it into your function as a plain string argument, and you do not have to
parse the URL yourself. This is the same mechanism you'll use in Day 3 and Day 4 for
routes like `/documents/{doc_id}` — one path parameter standing in for "which record."

## 1. Add the route

Add this below the `/` route:

```python
@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    status = SITE_STATUS[site_id.lower()]
    return {"site_id": site_id, "status": status}
```

`site_id: str` in the function signature is what tells FastAPI to capture that URL
segment as a string and hand it to you by name.

## Try it

Save, then request a site you know exists:

```bash
curl http://127.0.0.1:8000/sites/site-a/status
```

```json
{"site_id":"site-a","status":"On Track"}
```

Try a different case to confirm `.lower()` is doing its job:

```bash
curl http://127.0.0.1:8000/sites/SITE-B/status
```

```json
{"site_id":"SITE-B","status":"Delayed"}
```

Now try a site that does not exist:

```bash
curl -i http://127.0.0.1:8000/sites/site-x/status
```

You will get `HTTP/1.1 500 Internal Server Error`, and the `uvicorn` terminal will print
a `KeyError: 'site-x'` traceback. That is expected — you have not handled it yet. Keep
that terminal open; Step 5 exists to fix exactly this.

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


@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    status = SITE_STATUS[site_id.lower()]
    return {"site_id": site_id, "status": status}
```

</details>

This is an intermediate version — it does not yet match the reference implementation.
Step 5 changes the lookup line.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `422 Unprocessable Entity` | Requested `/sites//status` (empty `site_id`) | Supply a non-empty segment, e.g. `/sites/site-a/status` |
| Status comes back for the wrong site | Typo in the URL, or `SITE_STATUS` key spelling | Compare the URL segment against the dict keys in Step 3 |
| 500 error on every request, even known sites | Route defined before `SITE_STATUS`, or a typo in the dict | Recheck Step 3's checkpoint |

Next: **[Step 5 — Error Handling](05-error-handling.md)**.
