import json

from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"


# 1. The tool: a plain Python function. The model never runs this, our code does.
def get_order_status(order_id: str) -> str:
    orders = {
        "4821": "Shipped, arrives Thursday",
        "4822": "Packed, ships tomorrow",
    }
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


# 2. The tool description: the menu the model reads. It never sees the function above.
#    It answers three questions: what is the tool called, what does it do, what does it need?

# What it needs: one input called order_id, which is text.
inputs = {
    "type": "object",
    "properties": {
        "order_id": {"type": "string", "description": "The order number, for example 4821"},
    },
    "required": ["order_id"],
}

# What it is called and what it does. Say when to use it and when not to.
description = "Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."

# The tool list is a list because a model can be given many tools. Here there is only one.
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",  # same name as the Python function above
            "description": description,
            "parameters": inputs,
        },
    },
]

messages = [{"role": "user", "content": "Where is my order 4821?"}]
print("User:", messages[0]["content"], "\n")

# 3. First call: send the question together with the tool list.
response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
reply = response.choices[0].message

if reply.tool_calls:
    # The model did not answer. It asked us to run a tool.
    messages.append(reply)

    for call in reply.tool_calls:
        arguments = json.loads(call.function.arguments)
        print(f"Model asks for: {call.function.name}({arguments})")

        # 4. Our code runs the real function.
        result = get_order_status(**arguments)
        print("Tool returned:", result, "\n")

        # 5. Send the result back, tagged with the id of the request it answers.
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    # 6. Second call: the model reads the result and writes the final answer.
    response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    reply = response.choices[0].message

print("AI:", reply.content)
