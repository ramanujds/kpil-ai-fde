# Site Status API — Build Walkthrough

A step-by-step guide to hand-building the Site Status API from an empty folder. See
[../README.md](../README.md) for what the exercise is and why it exists in Day 1,
Block 3 (Python for AI).

## What You'll Build

A minimal FastAPI app, `main.py`, with two routes:

- `GET /` — a welcome message
- `GET /sites/{site_id}/status` — the status of a synthetic site, or a 404 if the site
  is unknown

You will build it twice: once set up with the traditional `venv` + `pip` workflow, once
with `uv`. The application code ends up identical either way — only the environment
setup and the run command differ.

## Who This Is For

Trainees with basic Python knowledge (variables, functions, `if` statements) and no
prior FastAPI experience. Also usable by a trainer as a live-demo script.

**Prerequisites:** Python 3.10+, uv, VS Code and Git already installed and working, per
[../../notes/02-setting-up-our-env.md](../../notes/02-setting-up-our-env.md). This
walkthrough does not repeat that setup — Step 1 below covers only what's new: turning an
empty folder into a running project, two different ways.

**Time:** about 25 to 30 minutes end to end.

## Steps

| Step | File | What you'll add | Est. time |
|---|---|---|---|
| 0 | [00-concepts-overview.md](00-concepts-overview.md) | Vocabulary and the shape of the finished app | 5 min |
| 1 | [01-environment-setup.md](01-environment-setup.md) | A runnable empty project, without uv and with uv | 8 min |
| 2 | [02-first-route.md](02-first-route.md) | The FastAPI app instance and the `/` route | 5 min |
| 3 | [03-in-memory-data.md](03-in-memory-data.md) | The `SITE_STATUS` dict | 2 min |
| 4 | [04-site-status-route.md](04-site-status-route.md) | The `/sites/{site_id}/status` route, happy path | 6 min |
| 5 | [05-error-handling.md](05-error-handling.md) | A 404 for an unknown site | 5 min |
| 6 | [06-recap-and-exercises.md](06-recap-and-exercises.md) | Review and practice | 5 min |

## Relationship to the Reference Implementation

By the end of Step 5, your `main.py` should match both of these exactly (they are
identical files, one per setup track):

- [../exercise/without-uv/main.py](../exercise/without-uv/main.py)
- [../exercise/with-uv/main.py](../exercise/with-uv/main.py)

Every checkpoint in this walkthrough was diffed against those files while writing it, so
if your file matches a checkpoint, it matches the reference.

## Suggested Demo Flow

- Run the empty app from Step 1 before writing a single route, and open `/docs` in a
  browser. Trainees immediately see that FastAPI gives you a working (if empty) server
  and interactive test page for free — it motivates the rest of the build.
- Have half the room follow the without-uv track and half follow with-uv (or have
  everyone do both, in two terminals side by side, per Step 1). The contrast lands
  better when trainees type both sets of commands themselves rather than being told
  about it.
- Before Step 5, deliberately request an unknown site (`/sites/site-x/status`) on the
  Step 4 version and let the room see the browser show "Internal Server Error" while the
  terminal prints a raw `KeyError` traceback. That failure is the motivation for the
  whole step — don't skip straight to the fix.
- After Step 4, pause and ask the room to predict what happens with a site that isn't in
  `SITE_STATUS`, before running it. It surfaces the gap Step 5 exists to close.

Start with [Step 0 — Concepts Overview](00-concepts-overview.md).
