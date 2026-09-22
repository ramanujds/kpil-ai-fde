# Step 2 — Project Setup With uv

> [Back to index](README.md) · Previous: [Concepts Overview](01-concepts-overview.md) · Next: [Same App, Same Code](03-same-app-same-code.md)

## Goal

Create `pyproject.toml` and let `uv sync` create the virtual environment and install
dependencies — compare directly against
[Step 2 of the without-uv walkthrough](../without-uv-walkthrough/02-environment-setup.md),
which did the same job in five manual steps.

## Why this matters

In the without-uv walkthrough, you had to: create a folder, create a venv, activate it,
write `requirements.txt`, then `pip install`. With `uv`, one file plus one command does
all of that. This isn't a different tool for a different job — it's the same job, with the
manual bookkeeping (did you activate? did you `pip freeze` after installing?) removed.
That gap is exactly what makes `uv` worth introducing on Day 1, before you're managing
dependencies for LLM SDKs and agent frameworks later in the program.

## 1. Create the project folder

```bash
mkdir site-status-api-with-uv
cd site-status-api-with-uv
```

## 2. Create `pyproject.toml`

```toml
[project]
name = "site-status-api"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
]
```

This is the same information `requirements.txt` held — the package list — plus the
project's name and required Python version in one place.

## 3. Sync

```bash
uv sync
```

`uv` creates `.venv` and installs `fastapi` and `uvicorn[standard]` into it. There is no
separate "activate" step, and no requirements file to keep in sync with what's actually
installed.

## Try it

```bash
uv run python -c "import fastapi; print(fastapi.__version__)"
```

Expect a version number printed, with no `ModuleNotFoundError` — and notice you never
activated anything.

## Checkpoint

<details>
<summary>Full <code>pyproject.toml</code></summary>

```toml
[project]
name = "site-status-api"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
]
```

</details>

This matches [../solutions/with-uv/pyproject.toml](../solutions/with-uv/pyproject.toml) exactly.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `uv: command not found` | `uv` isn't installed, or the terminal wasn't reopened after installing | See the install step in [the environment setup note](../../notes/02-setting-up-our-env.md) |
| `uv sync` fails on a syntax error | A typo in `pyproject.toml`'s TOML syntax (e.g. missing comma in the dependencies list) | Match the checkpoint above exactly |
| Old habit: manually creating and activating `.venv` | Muscle memory from the without-uv walkthrough | Skip it — `uv sync` and `uv run` handle the venv for you |

Next: **[Step 3 — Same App, Same Code](03-same-app-same-code.md)**.
