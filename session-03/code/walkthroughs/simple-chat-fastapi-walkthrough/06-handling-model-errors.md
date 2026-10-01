# Step 6 — Handling Model Errors

> Back to index · Previous: Adding Chat History · Next: The Chat Page

## Goal

Turn "the model cannot be reached" from a crash into a clear 503 response with a message.

## Why this matters

The model is a separate program that can be stopped, still loading or out of memory. In
`simple-chat` that crashed the script, which was acceptable for one person at a terminal.
A web service has other people's pages calling it, and a raw 500 error with a stack trace
tells them nothing.

The right answer is a status code that says what happened. 503 means "service unavailable":
your API is fine, but something it depends on is not. The page can show the message to the
user instead of freezing.

The order you built in Step 5 now pays off. The model call is the only thing that can fail,
and it happens before anything is saved. A failed question never reaches the history.

## 1. Add the Imports

Change the first import line and add the OpenAI error class:

```python
from fastapi import FastAPI, HTTPException
```

```python
from openai import OpenAI, OpenAIError
```

`HTTPException` is how a FastAPI function says "stop here and answer with this status".
`OpenAIError` is the base class of the SDK's errors, including connection failures.

## 2. Wrap the Model Call

In `chat`, replace the model call with:

```python
    try:
        response = client.chat.completions.create(model=MODEL, messages=new_messages)
    except OpenAIError as error:
        raise HTTPException(status_code=503, detail=f"Could not reach the model: {error}")
```

If the call works, the function carries on to `answer = ...` as before. If it fails,
`HTTPException` ends the function immediately, so the two `append` lines never run.

## Try it

Quit the Ollama app, then send a message from Swagger:

```json
{"detail": "Could not reach the model: Connection error."}
```

The status is 503. Open `GET /history` and confirm the failed question is not in it. Start
Ollama again, resend, and the chat works.

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI, HTTPException
from openai import OpenAI, OpenAIError
from pydantic import BaseModel

app = FastAPI(title="Simple Chat API")

# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"

# The chat history. It lives at module level, so it keeps growing while the
# server runs. There is one shared conversation for everyone using this server.
messages = []


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    # The history plus the new question. It is only saved if the model answers.
    new_messages = messages + [{"role": "user", "content": request.message}]

    try:
        response = client.chat.completions.create(model=MODEL, messages=new_messages)
    except OpenAIError as error:
        raise HTTPException(status_code=503, detail=f"Could not reach the model: {error}")

    answer = response.choices[0].message.content

    messages.append({"role": "user", "content": request.message})
    messages.append({"role": "assistant", "content": answer})

    return {"answer": answer}


@app.get("/history")
def get_history():
    return messages


@app.delete("/history")
def clear_history():
    messages.clear()
    return {"status": "cleared"}
```

</details>

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Still a 500 when Ollama is off | Caught a different exception, or the `try` does not wrap the model call | Catch `OpenAIError` around `client.chat.completions.create` |
| `NameError: HTTPException` | Forgot to import it | Add it to the `fastapi` import |
| Wrong status in the response | Used `return` instead of `raise` | Use `raise HTTPException(...)` |
| Failed question appears in history | The appends sit above the `try` | Keep the appends after the model call |

Next: **Step 7 — The Chat Page**.
