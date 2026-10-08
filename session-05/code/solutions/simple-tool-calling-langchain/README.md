# Simple Tool Calling with LangChain

The `simple-tool-calling` project rebuilt with LangChain. Same app, same two-call round trip, so you can see exactly what LangChain changes. Every line that differs from `simple-tool-calling` is marked with a `CHANGED` comment in the code.

## Prerequisites

1. **uv**, the Python package manager.
2. An OpenAI key. Copy `.env.example` to `.env` and paste the key in. `.env` is ignored by Git.

## Run

```
uv sync
uv run tool_calling.py
```

Expected output (the final wording will vary):

```
User: Update the order 4821 to Delivered, arrives Thursday

Model asks for: update_order_status({'order_id': '4821', 'status': 'Delivered, arrives Thursday'})
Tool returned: Order 4821 is now: Delivered, arrives Thursday

AI: Order 4821 has been updated to "Delivered, arrives Thursday".
```

The project has three tools (`get_order_status`, `update_order_status`, `cancel_order`). Change the question in `tool_calling.py` ("Where is my order 4821?", "Cancel order 4822") and the model picks a different tool each time, without any change to the loop.

## What Changed

| Area | Plain SDK (`simple-tool-calling`) | LangChain (this project) |
|---|---|---|
| Packages | `openai`, `python-dotenv` | `langchain-openai`, `python-dotenv` |
| Create the model | `OpenAI()` | `ChatOpenAI(model="gpt-4o-mini")` |
| Describe the tool | A hand-written nested dict (`inputs`, `description`, `tools`) | `@tool` above the function. The docstring and type hints do the job |
| Give the tools to the model | `tools=tools` on every call | `model.bind_tools(tools)` once |
| Send a question | `client.chat.completions.create(model=..., messages=..., tools=...)` | `model_with_tools.invoke(messages)` |
| The user message | `{"role": "user", "content": ...}` | `HumanMessage(...)` |
| Read the tool request | `json.loads(call.function.arguments)`, `call.function.name` | `call["args"]` (already a dict), `call["name"]` |
| Pick and run the tool | `get_order_status(**arguments)`, tool hardcoded | `tools_by_name[call["name"]].invoke(call["args"])`, tool chosen by the name the model sent |
| Send the result back | `{"role": "tool", "tool_call_id": ..., "content": ...}` | `ToolMessage(result, tool_call_id=call["id"])` |
| Read the answer | `reply.content` | `reply.content` |

## What Did Not Change

- The fake order table.
- The two-call round trip: ask, run the tool, send the result, get the answer.
- The model's reply has no text when it asks for a tool, so check `tool_calls` first.
- Your code, not the model, runs the tool. That is where checks and approvals go.

## Choosing the Tool by Name

The model replies with a tool name as plain text, for example `"update_order_status"`. Calling `get_order_status.invoke(...)` directly would run that one tool no matter what the model asked for. Instead, the code builds a dictionary once, `tools_by_name = {t.name: t for t in tools}`, and looks the tool up with `call["name"]`. Adding a fourth tool means adding it to the `tools` list and nothing else. If the model sends a name that is not in the dictionary, the code returns an "Unknown tool" message rather than crashing.

## Why the Description Matters Even More Here

`@tool` hides the nested dict, but the model still reads a description. LangChain builds it from your docstring, so a vague docstring gives a vague tool. Keep the "use when" and "do not use for" sentences.

## One Thing You Give Up

The plain SDK version describes the input too: "The order number, for example 4821". With a bare `@tool`, LangChain sends only the input's name and type (`order_id`, text), because the docstring above the function has no per-input notes. For one obvious input that is fine. For inputs the model could misread, either say more in the docstring or use `@tool(parse_docstring=True)` with an `Args:` section, which turns each input's note into its description.
