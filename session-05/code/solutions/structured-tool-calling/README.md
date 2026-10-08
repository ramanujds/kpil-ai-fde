# Structured Tool Calling

The same order-status example as `simple-tool-calling`, with Pydantic added so that every
handover in the loop has a checked shape.

| Where | Before (simple version) | Now |
|---|---|---|
| Tool inputs | A hand-written JSON schema, then `json.loads` | `OrderLookup` model: generates the schema and validates the model's arguments |
| Tool results | A plain string | `ToolResult` model: `ok`, `data`, `message`, `source` |
| Final answer | Free text | `OrderAnswer` model: order id, status, `needs_human`, reply |
| Bad input from the model | Would crash or run with bad values | Error text is sent back to the model so it can retry |
| Loop | Exactly two calls | Up to `MAX_ROUNDS` calls, so a retry is possible but capped |

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you do not have it.
2. Copy `.env.example` to `.env` and put your OpenAI key in it. Never commit `.env`.
3. Install dependencies:

```
uv sync
```

## Run

```
uv run structured_tool_calling.py
```

Expected output (the final wording will vary):

```
User: Where is my order 4821?

Model asks for: get_order_status({"order_id":"4821"})
Tool returned: {"ok":true,"data":{"order_id":"4821","status":"shipped","note":"Arrives Thursday"},"message":"","source":"order system"}

Structured answer: {
  "order_id": "4821",
  "status": "shipped",
  "needs_human": false,
  "reply": "Your order 4821 has shipped and will arrive on Thursday."
}

AI: Your order 4821 has shipped and will arrive on Thursday.
```

## How It Works

- `pydantic_function_tool(OrderLookup, ...)` builds the tool list from the model. The class
  docstring becomes the tool description and the field descriptions become the input
  descriptions, so there is one place to edit.
- `run_tool` validates the arguments with `model_validate_json` before the real function runs.
  On a `ValidationError` it returns the error text as a normal tool result, and the model
  gets another chance on the next round.
- `client.chat.completions.parse` with `response_format=OrderAnswer` makes the model's final
  answer arrive as a validated `OrderAnswer` object.
- `MAX_ROUNDS` stops the loop if the model never produces a valid answer.

The OpenAI tool list is built in strict mode, so the model is already steered towards the
schema and bad inputs are rare. The check in `run_tool` stays anyway: providers and models
differ, and a reply that fits the schema can still break a rule.

## Try It

- Change the pattern on `order_id` to `^\d{6}$` and ask about order 4821. The model's input
  now fails validation. Watch the error go back to the model and how it reacts.
- Ask about order 9999. The tool returns `ok: false` with a readable message, and the final
  answer should show `status: not_found`.
- Ask "Hi, how are you?" The model answers directly, and the answer still arrives in the
  `OrderAnswer` shape. Notice what it puts in `order_id` and `status`.
- Add a `priority` field to `OrderLookup` as one of `low`, `medium` or `high` with a default,
  and see how it appears in the tool request.
- Set `MAX_ROUNDS` to 1 and see what happens when the model needs a tool.
