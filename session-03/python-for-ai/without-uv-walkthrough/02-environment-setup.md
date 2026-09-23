# Step 2 — Environment Setup

> Back to index · Previous: Concepts Overview · Next: First Route

## Goal

Create an isolated virtual environment for this project and install FastAPI and Uvicorn
into it with `pip`.

## Why this matters

If you installed packages globally, every project on your machine would have to agree on
one version of every package, forever. A virtual environment gives each project its own
private copy, so this exercise's FastAPI version can never collide with a different
version some other project needs. This is the traditional, manual way to get that
isolation — `venv` creates the folder, `pip` installs into it. The sibling walkthrough
shows how `uv` collapses these same guarantees into fewer commands; you're doing it by
hand once here so the comparison actually means something.

## Steps

1. Create a project folder and move into it:

   ```bash
   mkdir site-status-api-without-uv
   cd site-status-api-without-uv
   ```

2. Create the virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. Activate it:

   ```bash
   source .venv/bin/activate       # macOS / Linux
   .venv\Scripts\activate          # Windows
   ```

   Your shell prompt should now show `(.venv)` at the start of the line.

4. Create `requirements.txt`:

   ```text
   fastapi
   uvicorn[standard]
   ```

5. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Try it

```bash
pip list
```

Expect `fastapi` and `uvicorn` in the list. If they're missing, the venv likely isn't
activated — check for `(.venv)` in your prompt and re-run step 3.

## Checkpoint

<details>
<summary>Full <code>requirements.txt</code></summary>

```text
fastapi
uvicorn[standard]
```

</details>

This matches the without-uv reference project's `requirements.txt` exactly.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `pip install` succeeds but `import fastapi` still fails later | Venv wasn't activated before installing | Activate first (`source .venv/bin/activate`), then reinstall |
| `python3: command not found` | System uses `python` instead of `python3` | Try `python -m venv .venv` instead |
| Prompt never shows `(.venv)` | Activation script wasn't sourced correctly | Re-run the exact activate command for your shell/OS from step 3 |

Next: **Step 3 — First Route**.
