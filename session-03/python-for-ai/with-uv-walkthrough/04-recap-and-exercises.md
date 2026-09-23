# Step 4 — Recap and Exercises

> [Back to index](README.md) · Previous: [Same App, Same Code](03-same-app-same-code.md)

## Quick reference

| Concept | Where it lives |
|---|---|
| Dependency list + project metadata | `pyproject.toml` |
| Exact installed versions, for reproducibility | `uv.lock` (written automatically by `uv sync`) |
| Create/update the venv and install everything | `uv sync` |
| Run a command inside this project's venv | `uv run <command>` |
| Application code | `main.py` — unchanged from the without-uv version |

## Tradeoffs: venv + pip vs. uv

| | `venv` + `pip` | `uv` |
|---|---|---|
| Files to maintain | `requirements.txt` (no built-in lock guarantee) | `pyproject.toml` + `uv.lock` |
| Steps to set up | Create venv, activate, install (3 commands) | `uv sync` (1 command) |
| Steps to run | Activate, then run | `uv run <command>` (no separate activate) |
| Reproducible versions across machines | Only if you manually `pip freeze` and commit it | Automatic, via `uv.lock` |
| What you give up | Nothing — it's the Python standard library tool, always available | A dependency on a third-party tool being installed |
| Learning curve | One tool most tutorials already assume | One more tool name to learn, fewer steps once learned |

## Gotchas

| Gotcha | Why it happens | Fix |
|---|---|---|
| `uv: command not found` | `uv` not installed, or terminal not reopened after install | Revisit [the environment setup note](../../../session-01/notes/02-setting-up-our-env.md) |
| Forgetting `uv run` and typing `uvicorn` directly | Old `venv` habit | Prefix every command with `uv run` in a `uv` project |
| Confusing `pyproject.toml` with `uv.lock` | Both mention dependencies | `pyproject.toml` is what you edit; `uv.lock` is generated, don't hand-edit it |

## Discussion questions

1. `main.py` never changed between the two walkthroughs. What does that tell you about
   where dependency management should sit relative to application code?
2. What problem does `uv.lock` solve that a loose `requirements.txt` doesn't? When would
   that difference actually matter on a real team?
3. Both approaches reach the exact same running app. What's the actual cost of the extra
   manual steps in the `venv` + `pip` flow — is it just typing, or something else?

## Exercises

1. Delete `.venv` and `uv.lock`, then run `uv sync` again — confirm it rebuilds both from
   `pyproject.toml` alone.
2. Add a new dependency (for example `httpx`) to `pyproject.toml` by hand, run `uv sync`,
   and check that `uv.lock` picked up an exact version for it.
3. Repeat exercises 1-3 from
   [the without-uv recap](../without-uv-walkthrough/07-recap-and-exercises.md) here —
   confirm the same code changes work unchanged under `uv run`.
4. Time yourself setting up this project from an empty folder with `uv`, then time the
   without-uv setup from scratch in a separate folder. Compare.
5. Rebuild `pyproject.toml` from memory in a new folder, then diff it against
   [../solutions/with-uv/pyproject.toml](../solutions/with-uv/pyproject.toml).

## What's next

Both Site Status API variants are done. The `uv` workflow here is the same one from Day 1's
environment checklist in
[`session-01/notes/02-setting-up-our-env.md`](../../../session-01/notes/02-setting-up-our-env.md)
— you'll reuse it for the rest of today's build: the LLM client, structured outputs and
function calling.
