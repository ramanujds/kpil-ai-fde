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
