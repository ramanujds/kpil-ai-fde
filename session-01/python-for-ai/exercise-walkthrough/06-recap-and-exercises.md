# Step 6 — Recap and Exercises

> [Back to index](README.md) · Previous: [Step 5 — Error Handling](05-error-handling.md)

## Quick Reference

| Concept | Where it lives |
|---|---|
| App instance | `app = FastAPI(title=...)` in [02-first-route.md](02-first-route.md) |
| A route | `@app.get("/")` in [02-first-route.md](02-first-route.md) |
| In-memory data | `SITE_STATUS` dict in [03-in-memory-data.md](03-in-memory-data.md) |
| Path parameter | `{site_id}` in [04-site-status-route.md](04-site-status-route.md) |
| Structured error | `HTTPException` in [05-error-handling.md](05-error-handling.md) |
| venv + pip vs. uv | [01-environment-setup.md](01-environment-setup.md) |

## Gotchas

| Gotcha | Why it happens |
|---|---|
| `--reload` sometimes misses a save | Rare, but if behavior doesn't match your latest edit, stop (`Ctrl+C`) and restart `uvicorn` |
| `site_id.lower()` vs. dict keys | `SITE_STATUS` keys are already lowercase; forgetting `.lower()` on the incoming value breaks mixed-case URLs like `/sites/SITE-A/status` |
| `requirements.txt` has no lockfile | Pinned versions (`==`) reduce drift, but two installs months apart can still pull different transitive dependencies; `uv.lock` (with-uv track) pins the whole tree |

## Discussion Questions

1. What would break if `SITE_STATUS` were replaced with a real database? What would stay
   the same in `main.py`?
2. Why does `dict.get(key)` returning `None` matter here, compared to `dict[key]`
   raising `KeyError`?
3. `HTTPException(status_code=404, ...)` — what would change, in behavior and in
   meaning, if you used `400` instead? What about `500`?
4. Both setup tracks produce the exact same `main.py`. What does that tell you about
   where "the app" actually lives, versus where "the environment" lives?

## Exercises

1. **Add a third route**, `GET /sites`, that returns the full `SITE_STATUS` dict as-is.
2. **Add a fourth site** to `SITE_STATUS` (pick any name and status) and confirm you can
   fetch its status without restarting the server manually (reload should pick it up).
3. **Change the error message** so a 404 also lists the valid site IDs, e.g.
   `"Unknown site 'site-x'. Known sites: site-a, site-b, site-c"`.
4. **Add a query parameter**: make `GET /sites/{site_id}/status` accept an optional
   `?verbose=true` and, when set, include a `"checked_at"` field with any fixed string
   value (no real timestamps needed for this exercise).
5. **Rebuild `main.py` from memory** in a fresh folder, without looking at the
   checkpoints, then diff it against
   [../exercise/with-uv/main.py](../exercise/with-uv/main.py). Resolve every
   difference before moving on.

## What's Next

This block feeds directly into Block 4, LLM APIs Overview, later today — the same
"function handles a request, returns structured data, fails clearly" shape reappears
there as a wrapper around an LLM API call instead of a dict lookup.
