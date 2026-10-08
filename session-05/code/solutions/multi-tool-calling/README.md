# Multi-Tool Calling

Builds on the simple tool-calling example. Two tools instead of one, and the code no longer
names the tool it runs. The model picks, and our code looks the function up by name.

The change from the single-tool version is small:

| Single tool | Multiple tools |
|---|---|
| `get_order_status(**arguments)` written directly in the code | `TOOL_FUNCTIONS[call.function.name](**arguments)` looked up from a registry |
| One round: ask, run, answer | A loop: ask, run, ask again, until the model answers |
| Assumes the name and arguments are valid | Unknown names and bad arguments come back to the model as readable messages |

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you do not have it.
2. Copy `.env.example` to `.env` and put your OpenAI key in it. Never commit `.env`.
3. Install dependencies:

```
uv sync
```

## Run

```
uv run multi_tool_calling.py
```

Expected output (the final wording will vary, and the model may call both tools in one round
or one after the other):

```
User: Where is my order 4821? And if it is a laptop, can I return it?

Model asks for: get_order_status({"order_id":"4821"})
Tool returned: Shipped, arrives Thursday

Model asks for: get_return_policy({"item_type":"laptop"})
Tool returned: Laptops can be returned within 10 days if sealed or unused.

AI: Your order 4821 has shipped and arrives Thursday. Laptops can be returned within 10 days if sealed or unused.
```

## Try It

- Ask only "What is your return policy for clothing?" The model picks the second tool and
  never touches the first.
- Ask "Hi, how are you?" Neither tool is called.
- Add a third tool. You need three things: the function, one line in `TOOL_FUNCTIONS`, and
  one entry in `tools`. The loop does not change.
- Remove a key from `TOOL_FUNCTIONS` but leave it in `tools`. The model asks for a tool that
  is not registered, and the "Unknown tool" message goes back to it.
- Make both descriptions vague and see how often the model picks the wrong tool.
