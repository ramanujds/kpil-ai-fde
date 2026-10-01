# Step 4 — The Chat Endpoint

> Back to index · Previous: Your First Endpoint · Next: Adding Chat History

## Goal

Add `POST /chat`: it takes a message in the request body, sends it to the model and returns
the answer. There is no memory yet.

## Why this matters

This step carries the two ideas that make an API different from a script.

First, the input arrives as data from outside, so it needs checking before your code uses
it. Declaring a small class describing the request lets FastAPI reject a bad request, such
as a missing `message`, with a clear error before your function even starts.

Second, the model call is the same one from `simple-chat`. Only its surroundings changed:
the question comes from a request instead of `input()`, and the answer goes into a response
instead of `print()`.

## 1. Add the Imports, the Client and the Model

Add to the top of `main.py`, and below the `app = ...` line:

```python
from openai import OpenAI
from pydantic import BaseModel
```

```python
# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"
```

Keep the imports together at the top; the client and `MODEL` go under `app`.

## 2. Describe the Request Body

```python
class ChatRequest(BaseModel):
    message: str
```

This says "a chat request is an object with a text field called `message`". FastAPI
validates incoming JSON against it and turns a valid one into a `ChatRequest` object.

## 3. Add the Endpoint

```python
@app.post("/chat")
def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": request.message}],
    )

    return {"answer": response.choices[0].message.content}
```

Because `request` is typed as `ChatRequest`, FastAPI reads the request body for it. The
text is `request.message`. The messages list has one item, just like the first `simple-chat`.

## Try it

With the server still running, open http://127.0.0.1:8000/docs, expand `POST /chat`, choose
"Try it out" and send:

```json
{"message": "Say hello in five words"}
```

```json
{"answer": "Hello, it's nice to meet you!"}
```

Now send `{}` instead. FastAPI answers with status 422 and a body saying `message` is
required. Your function never ran. That is the schema doing its job.

Finally send `{"message": "My name is Asha"}` and then `{"message": "What is my name?"}`.
The model does not know, because each request carries only one message.

## Checkpoint

<details>
<summary>Full <code>main.py</code></summary>

```python
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI(title="Simple Chat API")

# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": request.message}],
    )

    return {"answer": response.choices[0].message.content}
```

</details>

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| 422 on every request | Body sent without a `message` field, or not as JSON | Send `{"message": "..."}` |
| 500 with `Connection error` in the terminal | Ollama is not running | Start Ollama. Step 6 turns this into a friendly error |
| `POST /chat` missing from `/docs` | Used `@app.get` or forgot the decorator | Use `@app.post("/chat")` |
| 500 about the model not found | `MODEL` differs from what `ollama list` shows | Pull the model or fix the name |

Next: **Step 5 — Adding Chat History**.
