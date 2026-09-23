# Step 1 — Concepts Overview

> [Back to index](README.md) · Next: [Environment Setup](02-environment-setup.md)

## Goal

Get the vocabulary straight before touching any code, so the steps that follow read as
"adding one more familiar piece" instead of a list of unexplained commands.

## Why this matters

Every AI tool you'll build in this program — the LLM API calls later today, a RAG
lookup on Day 4, an agent "tool" on Day 5 — takes the same basic shape: **receive a
request, do a small piece of work, return structured data or a clear error.** A web API
is the simplest possible version of that shape, with no LLM involved yet, which is exactly
why it's the right first exercise. Learn the shape here, once, cleanly, and you'll
recognise it everywhere else it shows up.

## Vocabulary you need before Step 2

| Term | Plain-language meaning |
|---|---|
| API | A program that answers requests over the network with data (usually JSON), instead of a page a human reads in a browser. |
| Route | One specific URL path an API responds to, paired with an HTTP verb — e.g. `GET /` or `GET /sites/{site_id}/status`. |
| `GET` | The HTTP verb for "give me data," as opposed to `POST` (send data) or `DELETE` (remove something). Every route in this exercise is a `GET`. |
| Path parameter | A placeholder inside a route's path — `{site_id}` — filled in by whatever the caller puts in the URL, and handed to your function as an argument. |
| JSON | The text format APIs use to represent data — the same shape as a Python `dict`, which is why FastAPI can return a `dict` directly and it becomes JSON automatically. |
| Virtual environment | An isolated folder holding one project's Python packages, so installing something for this project can't collide with a different project's packages. |
| FastAPI | The Python library this exercise uses to turn plain functions into routes, with almost no boilerplate. |
| Uvicorn | The program that actually runs your FastAPI app and listens for requests — FastAPI describes the routes, Uvicorn serves them. |

## What's next

With that vocabulary in hand, Step 2 sets up an isolated environment for the project.

Next: **[Step 2 — Environment Setup](02-environment-setup.md)**.
