# Step 8 — Recap and Exercises

> Back to index · Previous: Adding Chat History

## Quick Reference

| Concept | Where it lives |
|---|---|
| Client (where requests go) | `OpenAI(...)` in `chat.py` and `chat_openai.py`; implicit in `ollama` |
| Model name | `MODEL` near the top of each file |
| Messages list | `messages=[...]` inside the loop |
| Reading the answer | `response.choices[0].message.content`, or `response.message.content` for `ollama` |
| Quitting | `if ... break` at the top of the loop |
| No memory | A new one-item `messages` list is built every turn (`chat.py`) |
| Memory | One `messages` list outside the loop, appended to every turn (`chat_with_history.py`) |
| Secrets | `.env` (ignored by Git), with `.env.example` as the template |

## Gotchas

| Gotcha | Why it happens |
|---|---|
| The model forgets your name | Each request carries only the latest question |
| The history version gets slower over a long chat | Every turn re-sends the whole conversation, so requests grow |
| History is gone after quitting | It lives in a Python list, which disappears when the program ends |
| `Connection error` on `chat.py` | Ollama is not running |
| `Missing credentials` on `chat_openai.py` | `.env` is missing or in the wrong folder |
| `EOFError` when input ends | The basic version does not handle Ctrl+D |
| Answers differ on every run | Models choose words with some randomness |

## Discussion Questions

1. For your fifth question in a chat, what exactly is in the `messages` list that gets sent?
2. Why can one SDK talk to both Ollama and OpenAI?
3. Where would you put the API key if you were working in a team, and where must it never go?
4. If the model has no memory, how does a chat website seem to remember you?
5. What would you need to send for the model to answer "What is my name?" correctly?
6. Why must the model's answer be added to the history too, not just the user's question?

## Exercises

1. Change `MODEL` in `chat.py` to another model you have pulled, and rerun.
2. Print `response.choices[0].finish_reason` after each answer. What does it say?
3. Add a `"system"` message before the user message to make the model answer in one sentence.
4. Make `chat.py` exit quietly on Ctrl+D by wrapping `input()` in `try`/`except EOFError`.
5. Move the model name and address in `chat.py` into the `.env` file and read them with `os.getenv`.
6. Print `len(messages)` after every turn in `chat_with_history.py`. How fast does it grow?
7. Rebuild `chat_with_history.py` from memory in an empty folder, then compare it with the reference.

## What's Next

The history lives only in memory, so it grows without limit and disappears when the program
ends. Natural next steps are trimming old messages, saving the history to a file, and giving
the model a system message that sets its behaviour.
