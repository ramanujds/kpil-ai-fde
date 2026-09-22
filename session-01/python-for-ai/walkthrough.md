# Walkthrough: Site Status API

**Day 1 | Block 3: Python for AI | Lab 2: Environment Setup**

> Goal: build and run a tiny FastAPI app two ways -- without uv, then with uv -- and feel
> the difference. About 15 to 20 minutes.

This walkthrough assumes you have already completed the base setup in
`session-01/notes/02-setting-up-our-env.md` (Python 3.10+, uv, VS Code, Git). If `uv --version`
does not work yet, do that first.

The solution exists on a separate `solutions` branch. Do not check it out until you have
tried each `TODO` yourself.

---

## Part A: Without uv

1. Open a terminal in `exercise/without-uv/`.
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Part B: With uv

1. Open a **second terminal** in `exercise/with-uv/` (leave Part A's terminal as it is,
   for comparison).
2. Sync the project's dependencies. uv reads `pyproject.toml`, creates `.venv`
   automatically, and installs into it:

   ```bash
   uv sync
   ```

---

## Part C: Fill In the TODOs

`main.py` is identical in both folders, so make your changes in **one** folder first,
get it working, then copy `main.py` over to the other.

### 1. The `/` route

```python
@app.get("/")
def root():
    return {"message": "Kalpataru Site Status API is running"}
```

### 2. The `/sites/{site_id}/status` route

```python
@app.get("/sites/{site_id}/status")
def get_site_status(site_id: str):
    status = SITE_STATUS.get(site_id.lower())
    if status is None:
        raise HTTPException(status_code=404, detail=f"Unknown site '{site_id}'")
    return {"site_id": site_id, "status": status}
```

**Why it matters:** `raise HTTPException(...)` is FastAPI's version of the `try` /
`except` pattern you will see everywhere from Day 3 onward -- instead of letting a
missing lookup crash the app, you return a clear, structured error.

---

## Part D: Run and Test It

```bash
# without-uv/ (venv still active)
uvicorn main:app --reload

# with-uv/
uv run uvicorn main:app --reload
```

Each starts a server at `http://127.0.0.1:8000`. With the app running, try any of these:

- Open `http://127.0.0.1:8000/docs` in a browser -- FastAPI's free, interactive test page
- Or from a second terminal:

  ```bash
  curl http://127.0.0.1:8000/
  curl http://127.0.0.1:8000/sites/site-a/status
  curl http://127.0.0.1:8000/sites/site-x/status
  ```

The first two should return JSON with a 200 status; the last should return a 404 with
your error message. Stop the server with `Ctrl+C` when you are done, then repeat in the
other folder to confirm both tracks behave identically.

| | Without uv | With uv |
|---|---|---|
| Commands to get running | `venv` + `activate` + `pip install` | `uv sync` |
| Remember to activate/deactivate | Yes | No |
| Reproducible for a teammate | `requirements.txt` (no lockfile) | `uv.lock` (exact versions) |
| Run the app | `uvicorn main:app --reload` | `uv run uvicorn main:app --reload` |

---

## If You Get Stuck

| Symptom | Likely fix |
|---|---|
| `ModuleNotFoundError: fastapi` | Re-run `pip install -r requirements.txt` (without-uv) or `uv sync` (with-uv) |
| `uvicorn: command not found` | Confirm `.venv` is activated (`which uvicorn`), or use `uv run uvicorn ...` |
| Every route returns `null` | A `TODO` still ends in `pass` -- Python functions return `None` by default |
| `/sites/site-a/status` returns 404 | Check `site_id.lower()` matches a key in `SITE_STATUS` exactly |

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
