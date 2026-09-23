# Step 1 — Concepts Overview

> [Back to index](README.md) · Next: [Project Setup With uv](02-project-setup-with-uv.md)

## Goal

Learn the handful of `uv`-specific terms you need, on top of what you already learned
building [the without-uv version](../without-uv-walkthrough/01-concepts-overview.md).

## Why this matters

Everything about the API itself — routes, path parameters, the `SITE_STATUS` dict, the 404
handling — is already familiar from the without-uv walkthrough and does not change here.
The only thing this walkthrough teaches is a different way to describe and install a
project's dependencies. Keeping that distinction clear is the point: dependency management
is a layer *underneath* your application code, not part of it, and you should be able to
swap that layer without touching a single line of `main.py`.

## Vocabulary you need before Step 2

| Term | Plain-language meaning |
|---|---|
| `pyproject.toml` | A single file describing the project (name, Python version, dependencies) — replaces a loose `requirements.txt`. |
| `uv sync` | Reads `pyproject.toml`, creates `.venv` if it doesn't exist, and installs exactly the right packages. One command, no separate activate step. |
| `uv run` | Runs a command using this project's `.venv` automatically, without you activating anything first. |
| Lockfile (`uv.lock`) | A file `uv` writes recording the exact version of every package installed, so anyone who runs `uv sync` later gets identical versions — `requirements.txt` alone doesn't guarantee that. |

## What's next

With that vocabulary, Step 2 sets up the project with `uv` instead of `venv` + `pip`.

Next: **[Step 2 — Project Setup With uv](02-project-setup-with-uv.md)**.
