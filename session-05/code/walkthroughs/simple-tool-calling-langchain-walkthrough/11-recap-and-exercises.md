# Step 11 — Recap and Exercises

> Back to index · Previous: Ask a Human First

## Quick Reference

| Concept | Where it lives |
|---|---|
| The tool | `get_order_status`, a function with `@tool` above it |
| What the model reads about the tool | The function name, the type hints and the docstring |
| The tool list | `tools` |
| Attaching the tools to the model | `model.bind_tools(tools)` |
| The model's request for a tool | `reply.tool_calls`, a list of dictionaries with `name`, `args` and `id` |
| The values the model chose | `call["args"]`, already a dictionary |
| Name-to-tool lookup | `tools_by_name = {t.name: t for t in tools}` |
| Picking the tool | `tools_by_name.get(call["name"])` |
| Running the tool | `selected_tool.invoke(call["args"])` |
| Sending the result back | `ToolMessage(str(result), tool_call_id=call["id"])` |
| The final answer | `reply.content` once the model stops asking for tools |
| The conversation memory | `history`, a list that every message is appended to and that is sent on each call |
| The ground rules for the model | A `SystemMessage` at the start of `history` |
| Letting the model use tools repeatedly | `while reply.tool_calls:` |
| Which tools need a human | `NEEDS_APPROVAL`, a set of tool names |
| Asking the human | `approved_by_human(name, args)`, which returns `True` only for `y` or `yes` |
| Refusing a tool | A sentence as the `result`, still sent back as a `ToolMessage` |
| Secrets | `.env` (ignored by Git), with `.env.example` as the template |

## What You Gave Up and What You Gained

| Gained (code you no longer write) | Given up (visibility you no longer have) |
|---|---|
| The nested tool description dictionary | The description is built for you, so you must print `.description` and `.args` to see what the model sees |
| `json.loads` on the arguments | The raw JSON the API sent, unless you look for it |
| `tools=tools` on every call | A visible `tools` argument in the call. A forgotten `bind_tools` is easy to miss |
| Message dictionaries with `role` keys | Role names. `HumanMessage` and `ToolMessage` hide them |
| Per-input descriptions for free | A bare `@tool` sends only the input's name and type, so the "for example 4821" note is lost unless you add `parse_docstring=True` |

Nothing about the round trip became easier to reason about. It is still two calls, and your
code still runs the tool. LangChain removes typing, not steps.

## Gotchas

| Gotcha | Why it happens |
|---|---|
| `TypeError: 'StructuredTool' object is not callable` | `@tool` replaces the function with an object. Run it with `.invoke(...)` |
| The model never uses the tool | The docstring does not say when to use it, or does not match how users ask |
| The model sends a tool name you did not expect | The name is text a model wrote. Look it up with `.get` and handle `None` |
| The wrong tool runs | The loop names a tool by hand instead of using the name in the request |
| A 400 error on the second call | The model's reply or the `tool_call_id` is missing from `messages` |
| `reply.content` is empty on the first call | The model asked for a tool instead of answering. Check `tool_calls` first |
| A tool returns `None` and the model says "None" | A `@tool` function that forgets `return`. `str(result)` hides the bug by turning it into text |
| Answers differ on every run | Models choose words with some randomness |
| The model says "I have no function for that" on a general question | Small models treat the tool list as their only job. Add a system message that allows direct answers |
| The model forgets earlier turns | The call sent a new list, not `history` |
| A 400 error after answering `n` | The denial branch sent no `ToolMessage`. Every tool request needs a result, even a refusal |
| A risky tool runs without a question | Its name is missing from `NEEDS_APPROVAL`, or has a typo |
| The model asks again after a no | The system message does not tell it to accept a denial |

## Discussion Questions

1. Which two things did `@tool` read from the function to build the description, besides the
   docstring?
2. The loop used to name `get_order_status`. What exactly would have gone wrong with a second
   tool, and why would it not have raised an error?
3. Why is the tool lookup built from the same `tools` list as `bind_tools`, and not
   written separately?
4. Why does the unknown-tool guard send a sentence back to the model instead of raising an
   exception?
5. Asked to update an order, the model has only `get_order_status`. What tells you that it
   cannot do the update, and what are two ways it can respond?
6. Why is the approval check written in code instead of telling the model in the system
   message to ask before cancelling?
7. Why does a denied request still send a `ToolMessage` back, even though the tool never ran?
8. `approved_by_human` treats anything except `y` or `yes` as a no. What could go wrong if it
   were the other way round?
9. Which tools would you put in `NEEDS_APPROVAL` for an assistant that can also issue refunds
   and email customers? Which would you leave out?

## Exercises

1. In `tool_calling.py`, add `update_order_status(order_id, status)` above the `tools` list. It
   should change the `orders` table and **return a sentence** such as "Order 4821 is now:
   Delivered". Add it to the `tools` list and change nothing else, then ask "Update the
   order 4821 to Delivered, arrives Thursday". This is the payoff of Step 6.
2. In `tool_calling.py`, ask "Where is my order 4822?" and then "What is the capital of
   France?". Watch the `Model asks for` line appear for one and not the other, with no change
   to the loop.
3. Print `get_order_status.description` and `get_order_status.args`. Change one word in the
   docstring and watch the model's behaviour on "I want a refund for order 4821".
4. Remove the `return` from your new `update_order_status` tool. What does the model say, and
   why does `str(result)` hide the problem from the loop?
5. Switch `get_order_status` to `@tool(parse_docstring=True)` and add an `Args:` section to the
   docstring. Print `.args` and compare with Step 3.
6. Ask for two orders in one question: "Where are orders 4821 and 4822?". How many entries are
   in `reply.tool_calls`, and how many `ToolMessage` objects does the loop send back?
7. Rename a tool in `tools` without changing its function, for example with
   `@tool("order_lookup")`. Confirm the loop still works because the lookup uses the tool's
   name, not your function's name.
8. In `human_in_the_loop.py`, add `update_order_status` from Exercise 1 and put it in
   `NEEDS_APPROVAL`. Approve one update and deny another.
9. Change `approved_by_human` so a denial can carry a reason, for example by asking "Why not?"
   and returning it. Send the reason back to the model in the denial message.
10. Write each approval decision (tool, arguments, yes or no) to a file called
    `decisions.log`. Decide where in the loop the line belongs.
11. Rebuild `human_in_the_loop.py` from memory in an empty folder, then compare it with the
    reference.

## What's Next

This program has one risk rule: a fixed list of tools that need a yes. The guardrails-and-approvals
walkthrough takes the same loop and adds more kinds of checks around it, such as permissions and
limits, checks on the input and output, and a cap on the number of steps, with three tools of
different risk. The Day 5 Lab 1 agent builds on the same round trip with more tools such as the
Day 4 retriever.

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
