# Step 3 — Your First Endpoint

> Back to index · Previous: Project Setup · Next: The Chat Endpoint

## Goal

Create `main.py` with a running FastAPI app and one endpoint, start it with `fastapi dev`,
and explore it in the browser and in Swagger.

## Why this matters

Getting a server to start and answer is a separate problem from getting a model to answer.
Doing it first with a trivial endpoint means that when `/chat` misbehaves later, you already
know the server itself is fine.

FastAPI also gives you something for free: an interactive page at `/docs` listing every
endpoint, where you can click "Try it out" and send requests with no front end at all. You
will use it to test Steps 4 to 6 long before the chat page exists.

## 1. Create the App

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="Simple Chat API")
```

`app` is the object that collects your endpoints. The `title` only appears in `/docs`.

## 2. Add an Endpoint

```python
@app.get("/")
def home():
    return {"status": "ok"}
```

The line starting with `@` is a decorator. It tells FastAPI "when someone sends a GET
request to `/`, run the function below". Whatever the function returns is turned into JSON.

This is a placeholder. In Step 7 the same endpoint will return the chat page.

## 3. Start the Server

```bash
uv run fastapi dev
```

`fastapi dev` finds `main.py` and the `app` in it, starts the server and reloads it whenever
you save a file. Leave it running in its own terminal for the rest of the walkthrough.

## Try it

Open http://127.0.0.1:8000 in the browser:

```text
{"status":"ok"}
```

Then open http://127.0.0.1:8000/docs. You will see Swagger with one row, `GET /`. Click it,
choose "Try it out" and "Execute" to see the same response.

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI

app = FastAPI(title="Simple Chat API")


@app.get("/")
def home():
    return {"status": "ok"}
```

</details>

`main.py` is not final yet. Steps 4 to 7 keep adding to it.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Error: Path does not exist` or no app found | Running the command outside the project folder, or the file is not called `main.py` | `cd` into the project and check the file name |
| `Address already in use` | An older server is still running | Stop it with Ctrl+C, or close the other terminal |
| Page shows `Not Found` | Opened a path other than `/` or `/docs` | Use the exact addresses above |
| Edits do not show up | Server was started with plain `fastapi run` | Use `fastapi dev`, which reloads on save |

Next: **Step 4 — The Chat Endpoint**.
