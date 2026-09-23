# Step 7 — Recap and Exercises

> [Back to index](README.md) · Previous: [Error Handling](06-error-handling.md)

## Quick reference

| Concept | Where it lives |
|---|---|
| FastAPI app instance | `main.py`, `app = FastAPI(...)` |
| Route registration | `@app.get("/path")` above a function |
| Path parameter | `{site_id}` in the route path, `site_id: str` in the function signature |
| In-memory lookup | The `SITE_STATUS` dict |
| Clear error response | `HTTPException(status_code=404, detail=...)` |
| Isolated dependencies | `.venv` (created by `venv`) + `requirements.txt` (installed by `pip`) |

## Gotchas

| Gotcha | Why it happens | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | The venv isn't activated in the current terminal | `source .venv/bin/activate`, then reinstall if needed |
| `address already in use` on port 8000 | An earlier `uvicorn` process is still running | Stop it with `Ctrl+C`, or run with `--port 8001` |
| Code changes don't show up in responses | Server started without `--reload` | Restart with `uvicorn main:app --reload` |
| `500` instead of `404` for an unknown id | A route still indexes the dict directly instead of using `.get()` | Review [Step 6](06-error-handling.md) |

## Discussion questions

1. Why does the API return a `404` with a message instead of letting the `KeyError`
   crash the app? What would a caller — a script, or later, an AI agent calling this as a
   tool — do differently with each response?
2. What happens to `SITE_STATUS` the moment this process restarts? Where would this data
   actually live in a system used by more than one person?
3. Why is `site_id` typed as `str` in the function signature? What would break if a site
   id could also be written as a plain number?
4. Compare this `venv` + `pip` setup to the `uv` setup in
   [`session-01/notes/02-setting-up-our-env.md`](../../../session-01/notes/02-setting-up-our-env.md).
   Which manual steps did `uv` remove?

## Exercises

1. Add a fourth synthetic site to `SITE_STATUS` and confirm you can fetch its status.
2. Add a `GET /sites` route that returns every site's id and name, without its status.
3. Change the `404` message so it also lists the valid site ids a caller could try.
4. Add a `GET /sites/{site_id}` route (no `/status`) that returns a `400` — not a `404` —
   if `site_id` doesn't start with `"kpil-"`, so a malformed id is distinguished from an
   unknown one.
5. Close this file, rebuild `main.py` from memory in a new folder, then diff it against
   [../solutions/without-uv/main.py](../solutions/without-uv/main.py). Anything different is worth a second look.

## What's next

The [with-uv walkthrough](../with-uv-walkthrough/README.md) rebuilds this exact app with
`uv` instead of `venv` + `pip`, and calls out precisely what changes and what stays the
same.
