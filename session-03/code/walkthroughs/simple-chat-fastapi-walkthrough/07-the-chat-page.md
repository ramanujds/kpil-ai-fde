# Step 7 — The Chat Page

> Back to index · Previous: Handling Model Errors · Next: Recap and Exercises

## Goal

Create `static/index.html`, a one-page chat UI, and make `GET /` serve it.

## Why this matters

The API works, but nobody wants to chat through Swagger. The page is the second half of the
app: it turns typing into `POST /chat` requests and turns the replies back into bubbles.

The page holds no conversation of its own. It asks the server for it. On load it calls
`GET /history` and draws what comes back, which is why a refresh does not lose the chat.
When you send a message it draws your bubble at once, and the answer's bubble when the
server replies. That is the same split from Step 1: the server owns the data, the page
displays it.

The page is plain HTML and JavaScript in one file, with no build step and no framework, so
FastAPI can hand it over as an ordinary file. You are not here to learn JavaScript. Read
each snippet as "this line does what the matching Python step did".

## 1. Serve the Page from `/`

In `main.py`, add the import:

```python
from fastapi.responses import FileResponse
```

and replace the body of `home`:

```python
@app.get("/")
def home():
    return FileResponse("static/index.html")
```

`FileResponse` sends a file as it is. The path is relative to where you start the server,
so run `uv run fastapi dev` from the project folder. Also add the usage docstring at the
very top of `main.py`, above the imports:

```python
"""
Simple Chat API: the chat-with-history app as a web service with a one-page UI.

    GET    /           the chat page (static/index.html)
    POST   /chat       send a message, get the model's answer
    GET    /history    the complete conversation so far
    DELETE /history    start a new conversation

Run (from this folder):
    uv sync                    install the dependencies (first time only)
    uv run fastapi dev         start the server with auto-reload

Then open http://127.0.0.1:8000 for the chat, or /docs for Swagger.
"""
```

## 2. The Page Structure

Create the folder `static` and the file `static/index.html`. Start with the skeleton:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simple Chat</title>
</head>
<body>
  <h1>Simple Chat</h1>
  <div id="log"></div>
  <div id="error"></div>
  <form id="form">
    <input id="input" placeholder="Type a message" autocomplete="off" autofocus>
    <button type="submit" id="send">Send</button>
    <button type="button" id="clear">New chat</button>
  </form>
</body>
</html>
```

Three areas matter: `log` will hold the bubbles, `error` shows failures, and the form has
the input and two buttons. The `id` values are how the script will find them.

## 3. The Styling

Add inside `<head>`, after the `<title>` line:

```html
  <style>
    body { font-family: sans-serif; max-width: 700px; margin: 2rem auto; padding: 0 1rem; }
    #log { border: 1px solid #ccc; border-radius: 8px; height: 400px; overflow-y: auto; padding: 1rem; }
    .msg { margin: 0.5rem 0; padding: 0.5rem 0.75rem; border-radius: 8px; white-space: pre-wrap; max-width: 85%; }
    .user { background: #5B4A9E; color: #fff; margin-left: auto; }
    .assistant { background: #eee; }
    form { display: flex; gap: 0.5rem; margin-top: 1rem; }
    input { flex: 1; padding: 0.5rem; }
    button { padding: 0.5rem 1rem; }
    #error { color: #b00020; min-height: 1.5rem; }
  </style>
```

Purely cosmetic: the user's bubbles are purple and pushed right, the model's are grey. The
log scrolls when it fills up. Reload the page to see the layout, though sending does
nothing yet.

## 4. Find the Elements and Draw a Message

Add before `</body>`:

```html
  <script>
    const log = document.getElementById("log");
    const form = document.getElementById("form");
    const input = document.getElementById("input");
    const send = document.getElementById("send");
    const error = document.getElementById("error");

    // Add one message bubble to the conversation shown on the page.
    function show(role, text) {
      const div = document.createElement("div");
      div.className = "msg " + role;
      div.textContent = text;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
    }

    // On page load, fetch the complete conversation from the server.
    async function loadHistory() {
      const response = await fetch("/history");
      const history = await response.json();
      history.forEach(m => show(m.role, m.content));
    }
```

The first five lines grab the elements by their `id`. `show` makes a new `div`, gives it the
class `msg user` or `msg assistant` so the styling applies, fills in the text and appends it.
`textContent` is used rather than `innerHTML` so text from the model can never be run as
HTML. `loadHistory` calls `GET /history` and draws every message with `show`; it is called
at the end, in sub-step 6. Do not close the `<script>` tag yet.

## 5. Send a Message

Continue inside the script:

```html

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      error.textContent = "";
      show("user", text);
      input.value = "";
      send.disabled = true;

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail);
        show("assistant", data.answer);
      } catch (e) {
        error.textContent = e.message;
      }
      send.disabled = false;
      input.focus();
    });
```

Read it top to bottom. `preventDefault` stops the browser from reloading the page when the
form is submitted. Empty text is ignored. Your bubble is drawn immediately and the Send
button is disabled so a second click cannot send while the model is thinking. `fetch` then
does the `POST /chat` with the JSON body that `ChatRequest` expects from Step 4.

If the response is not a success, the `detail` from Step 6's 503 becomes an exception and
lands in the red error line. Whatever happens, the button is re-enabled at the end.

## 6. Load the History and Start a New Chat

Finish the script:

```html

    document.getElementById("clear").addEventListener("click", async () => {
      await fetch("/history", { method: "DELETE" });
      log.innerHTML = "";
      error.textContent = "";
    });

    loadHistory();
  </script>
```

The New chat button calls `DELETE /history` and then empties the log on screen. The last
line runs `loadHistory` as soon as the page loads, so any existing conversation is drawn.

## Try it

With the server running, open http://127.0.0.1:8000.

1. Type "My name is Asha" and press Enter. Your bubble appears, then the model's.
2. Type "What is my name?" The model answers correctly.
3. Press F5. The whole conversation comes back from `GET /history`.
4. Click New chat. The log clears. Refresh to confirm it stays empty.
5. Quit Ollama and send a message. The red line shows "Could not reach the model", and after
   restarting Ollama the same message works.

## Checkpoint

<details>
<summary>Full <code>static/index.html</code></summary>

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simple Chat</title>
  <style>
    body { font-family: sans-serif; max-width: 700px; margin: 2rem auto; padding: 0 1rem; }
    #log { border: 1px solid #ccc; border-radius: 8px; height: 400px; overflow-y: auto; padding: 1rem; }
    .msg { margin: 0.5rem 0; padding: 0.5rem 0.75rem; border-radius: 8px; white-space: pre-wrap; max-width: 85%; }
    .user { background: #5B4A9E; color: #fff; margin-left: auto; }
    .assistant { background: #eee; }
    form { display: flex; gap: 0.5rem; margin-top: 1rem; }
    input { flex: 1; padding: 0.5rem; }
    button { padding: 0.5rem 1rem; }
    #error { color: #b00020; min-height: 1.5rem; }
  </style>
</head>
<body>
  <h1>Simple Chat</h1>
  <div id="log"></div>
  <div id="error"></div>
  <form id="form">
    <input id="input" placeholder="Type a message" autocomplete="off" autofocus>
    <button type="submit" id="send">Send</button>
    <button type="button" id="clear">New chat</button>
  </form>

  <script>
    const log = document.getElementById("log");
    const form = document.getElementById("form");
    const input = document.getElementById("input");
    const send = document.getElementById("send");
    const error = document.getElementById("error");

    // Add one message bubble to the conversation shown on the page.
    function show(role, text) {
      const div = document.createElement("div");
      div.className = "msg " + role;
      div.textContent = text;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
    }

    // On page load, fetch the complete conversation from the server.
    async function loadHistory() {
      const response = await fetch("/history");
      const history = await response.json();
      history.forEach(m => show(m.role, m.content));
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      error.textContent = "";
      show("user", text);
      input.value = "";
      send.disabled = true;

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail);
        show("assistant", data.answer);
      } catch (e) {
        error.textContent = e.message;
      }
      send.disabled = false;
      input.focus();
    });

    document.getElementById("clear").addEventListener("click", async () => {
      await fetch("/history", { method: "DELETE" });
      log.innerHTML = "";
      error.textContent = "";
    });

    loadHistory();
  </script>
</body>
</html>
```

</details>

<details>
<summary>Full <code>main.py</code></summary>

```python
"""
Simple Chat API: the chat-with-history app as a web service with a one-page UI.

    GET    /           the chat page (static/index.html)
    POST   /chat       send a message, get the model's answer
    GET    /history    the complete conversation so far
    DELETE /history    start a new conversation

Run (from this folder):
    uv sync                    install the dependencies (first time only)
    uv run fastapi dev         start the server with auto-reload

Then open http://127.0.0.1:8000 for the chat, or /docs for Swagger.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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
    return FileResponse("static/index.html")


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

These match the reference project's `static/index.html` and `main.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Internal Server Error` on `/`, file not found in the terminal | Server started from a different folder, or the file is not at `static/index.html` | Run `uv run fastapi dev` from the project folder |
| Page loads but Send does nothing | A typo in the script, or the `<script>` block is outside `<body>` | Open the browser console (F12) and read the error |
| Your bubble appears but the answer never does | `/chat` returned an error | Check the red line and the server terminal |
| Page is blank white after editing | An unclosed tag in the HTML | Compare with the checkpoint |

Next: **Step 8 — Recap and Exercises**.
