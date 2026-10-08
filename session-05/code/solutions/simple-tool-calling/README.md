# Simple Tool Calling

The smallest possible tool-calling example. One tool, one question, two calls to the model.

The model never runs the tool. It asks for it, our code runs it, and the result goes back to
the model so it can write the answer.

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you do not have it.
2. Copy `.env.example` to `.env` and put your OpenAI key in it. Never commit `.env`.
3. Install dependencies:

```
uv sync
```

## Run

```
uv run tool_calling.py
```

Expected output (the final wording will vary):

```
User: Where is my order 4821?

Model asks for: get_order_status({'order_id': '4821'})
Tool returned: Shipped, arrives Thursday

AI: Your order 4821 has shipped and will arrive on Thursday.
```

## Try It

- Ask "Hi, how are you?" The model answers directly and never asks for the tool.
- Ask about order 9999. The tool returns a readable "not found" message, and the model
  passes it on.
- Change the tool description to something vague, like "Gets stuff", and see how the model's
  choice changes.
