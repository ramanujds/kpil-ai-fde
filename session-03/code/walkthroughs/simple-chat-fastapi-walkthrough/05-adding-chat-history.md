# Step 5 — Adding Chat History

> Back to index · Previous: The Chat Endpoint · Next: Handling Model Errors

## Goal

Make the model remember the conversation by keeping a `messages` list on the server, and add
`GET /history` and `DELETE /history` to read and reset it.

## Why this matters

In `simple-chat` the history was a list outside the `while` loop. A web server has no such
loop: every request starts a fresh call of your function, so a list created inside it would
vanish at once. The list must live where it survives between requests, at module level,
which Python runs once when the server starts.

Two consequences follow, and both should be said out loud. The history lives in memory, so
restarting the server clears it. And there is exactly one list, so everyone who uses this
server shares one conversation. That is fine for learning; a real app keeps one history per
user.

There is one more subtle point. The user's message should only be saved if the model
answers. Otherwise a failed request leaves a question in the history with no answer, and
the next request sends the model a conversation that never happened. Step 6 depends on this
order, so build it correctly now.

## 1. Create the History

Add below `MODEL = "llama3:8b"`:

```python
# The chat history. It lives at module level, so it keeps growing while the
# server runs. There is one shared conversation for everyone using this server.
messages = []
```

## 2. Send the History Plus the New Question

Replace the body of `chat` with:

```python
    # The history plus the new question. It is only saved if the model answers.
    new_messages = messages + [{"role": "user", "content": request.message}]

    response = client.chat.completions.create(model=MODEL, messages=new_messages)

    answer = response.choices[0].message.content

    messages.append({"role": "user", "content": request.message})
    messages.append({"role": "assistant", "content": answer})

    return {"answer": answer}
```

`messages + [...]` builds a new list and leaves `messages` untouched. Only after the model
has answered do the two `append` calls save the question and the answer, in that order.

## 3. Add the History Endpoints

```python
@app.get("/history")
def get_history():
    return messages


@app.delete("/history")
def clear_history():
    messages.clear()
    return {"status": "cleared"}
```

`GET /history` returns the list, which is what the page will use to redraw the conversation
after a refresh. `DELETE /history` empties it in place. `clear()` is used rather than
`messages = []` so that the module-level list itself is emptied; assigning a new list inside
a function would only create a local variable.

## Try it

In Swagger, send `{"message": "My name is Asha"}` and then `{"message": "What is my name?"}`.

```json
{"answer": "Your name is Asha!"}
```

Open `GET /history` and execute it:

```json
[
  {"role": "user", "content": "My name is Asha"},
  {"role": "assistant", "content": "Nice to meet you, Asha!"},
  {"role": "user", "content": "What is my name?"},
  {"role": "assistant", "content": "Your name is Asha!"}
]
```

Run `DELETE /history`, then `GET /history` again. It returns `[]`.

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

    response = client.chat.completions.create(model=MODEL, messages=new_messages)

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
| The model still forgets | Sent only the new message, not `new_messages` | Pass `messages=new_messages` |
| History empties after every edit | `fastapi dev` restarts the server on save, and the list lives in memory | Expected. Send your messages again |
| `DELETE /history` seems to do nothing | Used `messages = []` inside the function | Use `messages.clear()` |
| `GET /history` shows a user message with no answer | Appended the user message before the model call | Save both messages only after the answer arrives |

Next: **Step 6 — Handling Model Errors**.
