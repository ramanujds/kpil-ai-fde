# Step 1 — Environment Setup

> [Back to index](README.md) · Previous: [Step 0 — Concepts Overview](00-concepts-overview.md) · Next: [Step 2 — First Route](02-first-route.md)

## Goal

Get an empty FastAPI project installed and runnable, two different ways: the
traditional `venv` + `pip` workflow, and `uv`.

## Why this matters

Every Python project needs an isolated place to install packages, so one project's
dependencies never collide with another's. There is more than one way to create that
isolation, and the two you will meet constantly in this program — `venv`/`pip` and
`uv` — solve the same problem with a very different number of steps. Feeling that
difference on a two-file project, before you depend on it for anything real, is the
point of this step.

Do both tracks if you can — open two terminals side by side. If you only have time for
one, do `with-uv`; you will use `uv` for the rest of the program.

## 1. Without uv

Create a project folder and set up a virtual environment:

```bash
mkdir site-status-without-uv && cd site-status-without-uv
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

Create `requirements.txt`:

```text
fastapi==0.115.0
uvicorn==0.30.6
```

Install:

```bash
pip install -r requirements.txt
```

## 2. With uv

In a **second terminal**, create a separate project folder:

```bash
mkdir site-status-with-uv && cd site-status-with-uv
```

Create `pyproject.toml`:

```toml
[project]
name = "site-status-api"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.6",
]
```

Install — `uv sync` reads `pyproject.toml`, creates `.venv` automatically, and installs
into it:

```bash
uv sync
```

## Try it

Confirm each install worked. In the without-uv terminal (venv still active):

```bash
python -c "import fastapi; print(fastapi.__version__)"
```

In the with-uv terminal:

```bash
uv run python -c "import fastapi; print(fastapi.__version__)"
```

Both should print `0.115.0`.

## Checkpoint

<details>
<summary>Full <code>requirements.txt</code> (without-uv track)</summary>

```text
fastapi==0.115.0
uvicorn==0.30.6
```

</details>

<details>
<summary>Full <code>pyproject.toml</code> (with-uv track)</summary>

```toml
[project]
name = "site-status-api"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.6",
]
```

</details>

This matches [../exercise/without-uv/requirements.txt](../exercise/without-uv/requirements.txt)
and [../exercise/with-uv/pyproject.toml](../exercise/with-uv/pyproject.toml) exactly.

## What You Typed vs. What uv Did

| | Without uv | With uv |
|---|---|---|
| Commands to get installed | `venv` + `activate` + `pip install` | `uv sync` |
| Remember to activate/deactivate | Yes | No |
| Reproducible for a teammate | `requirements.txt` (no lockfile) | `uv.lock` (exact versions, generated automatically) |

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `command not found: uv` | uv not installed, or terminal opened before install | Reopen the terminal, or re-run the uv installer from `notes/02-setting-up-our-env.md` |
| `ModuleNotFoundError: fastapi` when running Python directly | Forgot to activate `.venv` (without-uv track) | Run `source .venv/bin/activate` again, confirm with `which python` |
| `uv sync` seems to do nothing | Already synced — this is correct, not an error | Continue; `uv sync` is safe to re-run any time |

Next: **[Step 2 — First Route](02-first-route.md)**.
