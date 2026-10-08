import json

from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"
MAX_ROUNDS = 5  # cap on model calls, so a stubborn model cannot loop forever

QUESTION = "Where is my order 4821? And if it is a laptop, can I return it?"


# 1. The tools: plain Python functions. The model never runs these, our code does.
def get_order_status(order_id: str) -> str:
    orders = {
        "4821": "Shipped, arrives Thursday",
        "4822": "Packed, ships tomorrow",
    }
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


def get_return_policy(item_type: str) -> str:
    policies = {
        "laptop": "Laptops can be returned within 10 days if sealed or unused.",
        "clothing": "Clothing can be returned within 30 days with tags attached.",
    }
    return policies.get(item_type.lower(), f"No return policy found for {item_type}.")


# 2. The registry: tool name -> Python function. This is what makes the code dynamic.
#    The model sends a name as text, and we look it up here instead of writing the name in code.
TOOL_FUNCTIONS = {
    "get_order_status": get_order_status,
    "get_return_policy": get_return_policy,
}

# 3. The menu the model reads: one entry per tool. Each name must match a key in the registry.
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds or returns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order number, for example 4821"},
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_return_policy",
            "description": "Look up the return policy for a type of item. Use when the customer asks whether or how they can return something. Do not use for delivery status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_type": {"type": "string", "description": "The kind of item, for example laptop or clothing"},
                },
                "required": ["item_type"],
            },
        },
    },
]


def run_tool(name: str, raw_arguments: str) -> str:
    # 4. Find the function by the name the model gave us. The model can ask for a name that
    #    does not exist or send arguments that do not fit, so every failure becomes a readable
    #    message that goes back to the model instead of crashing the program.
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return f"Unknown tool '{name}'. Available tools: {', '.join(TOOL_FUNCTIONS)}."
    try:
        arguments = json.loads(raw_arguments)
        return function(**arguments)
    except (json.JSONDecodeError, TypeError) as error:
        return f"Could not run {name} with those arguments: {error}"


messages = [{"role": "user", "content": QUESTION}]
print("User:", QUESTION, "\n")

# 5. The loop: keep going until the model answers instead of asking for a tool.
#    One question may need one tool, several tools at once, or one tool after another.
for _ in range(MAX_ROUNDS):
    response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    reply = response.choices[0].message

    if not reply.tool_calls:
        print("AI:", reply.content)
        break

    # The model did not answer. It asked us to run one or more tools.
    messages.append(reply)
    for call in reply.tool_calls:
        print(f"Model asks for: {call.function.name}({call.function.arguments})")

        result = run_tool(call.function.name, call.function.arguments)
        print("Tool returned:", result, "\n")

        # Send the result back, tagged with the id of the request it answers.
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
else:
    print("Gave up: no final answer after", MAX_ROUNDS, "rounds. Hand this one to a person.")
