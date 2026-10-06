# Step 8 — Recap and Exercises

> Back to index · Previous: Run the Tool and Return the Result

## Quick Reference

| Concept | Where it lives |
|---|---|
| The tool (a plain function) | `get_order_status` |
| What the tool needs | `inputs` |
| What the tool does and when to use it | `description` |
| The list the model is given | `tools` |
| The model's request for a tool | `reply.tool_calls` |
| The values the model chose | `json.loads(call.function.arguments)` |
| Running the tool | `get_order_status(**arguments)` |
| Sending the result back | A message with `"role": "tool"` and the request's `tool_call_id` |
| The final answer | `reply.content` after the second call |
| Secrets | `.env` (ignored by Git), with `.env.example` as the template |

## Gotchas

| Gotcha | Why it happens |
|---|---|
| `reply.content` is `None` | The model asked for a tool instead of answering. Text comes after the second call |
| The arguments are a string | The API sends JSON text; use `json.loads` |
| A 400 error on the second call | The conversation is missing the model's request or the `tool_call_id` |
| The model never uses the tool | The description does not say when to use it, or does not match how users ask |
| The model uses the wrong tool | Descriptions that are vague or overlap |
| The model invents an input | A required input is not clearly explained in `inputs` |
| The program only handles one round | A real agent loops until the model stops asking. This program makes exactly two calls at most |
| Answers differ on every run | Models choose words with some randomness |

## Discussion Questions

1. Which part of this program does the model do, and which part does your code do?
2. Why is the model's request added to `messages` before the tool result?
3. The model never sees `get_order_status`. What does it use to decide to call it?
4. What would happen if the description said only "Gets stuff"?
5. Where in the program would you add a check, a limit or a human approval before an action
   tool runs?
6. This tool only reads data. What changes if the tool were `issue_refund`?

## Exercises

1. Add a third order to the table in `get_order_status`, and ask about it.
2. Change the description to "Gets stuff". Run the same question several times and see
   whether the model still uses the tool.
3. Add `print(messages)` before the second call. Count the items and match them to the table
   in Step 7.
4. Add a second input, `customer_name`, to the tool in `inputs` and the function. What does
   the model do when the question does not include a name?
5. Wrap the function call in `try`/`except` and return a readable sentence if it fails.
   Test it by raising an error inside the function on purpose.
6. Add a second tool, `get_delivery_estimate`, to the `tools` list. Ask a question that fits
   each tool and see whether the model picks the right one.
7. Change the `for` loop so it also handles a tool name your code does not know, by sending
   back a tool message that says "Unknown tool".
8. Rebuild `tool_calling.py` from memory in an empty folder, then compare it with the
   reference.

## What's Next

This program makes at most two calls to the model, so it can use one tool once. A real
agent keeps going: it checks whether the answer is complete, calls more tools if needed and
stops only when it has what it needs. The Day 5 Lab 1 agent puts this same round trip inside
a loop, adds more tools such as the Day 4 retriever, and applies step limits. Block 3 adds
guardrails and approvals around the line where your code runs the tool.
