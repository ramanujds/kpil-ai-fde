# Step 5 — Site Status Route

> [Back to index](README.md) · Previous: [In-Memory Data](04-in-memory-data.md) · Next: [Error Handling](06-error-handling.md)

## Goal

Add `GET /sites/{site_id}/status`, which reads a path parameter and looks it up in
`SITE_STATUS` — happy path only for now.

## Why this matters

`{site_id}` in the route path is a placeholder: whatever text a caller puts there becomes
the `site_id` argument in your function, as a plain Python `str`. This is how a REST API
addresses one specific record out of many, instead of one endpoint per site. This step
deliberately stops at the happy path — you're about to see, in the next step, exactly what
goes wrong when a caller asks for something that doesn't exist, and why that matters.

## 1. Add the route

```python
@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    return SITE_STATUS[site_id]
```

Add this below the `read_root` function.

## Try it

```bash
curl http://127.0.0.1:8000/sites/kpil-01/status
```

Expect:

```json
{"name":"Ring Road Flyover","status":"on-track"}
```

Now try an id that isn't in the dict:

```bash
curl http://127.0.0.1:8000/sites/kpil-99/status
```

Expect an ugly result: a `500 Internal Server Error` with no useful message, because
`SITE_STATUS["kpil-99"]` raises a `KeyError` that nothing catches. Keep this failure in
mind — Step 6 exists specifically to fix it.

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


@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    return SITE_STATUS[site_id]
```

</details>

This is not the final version of `main.py` — the next step replaces the direct dict
lookup with something that fails cleanly.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `404 Not Found` on every request, even `kpil-01` | Route path typo, e.g. `/site/{site_id}/status` | Match the path exactly: `/sites/{site_id}/status` |
| `site_id` argument name doesn't match the path | Function parameter must match the `{...}` name in the decorator | Keep both spelled `site_id` |
| Server didn't pick up the new route | Uvicorn wasn't started with `--reload` | Restart with `uvicorn main:app --reload`, or save the file again |

Next: **[Step 6 — Error Handling](06-error-handling.md)**.
