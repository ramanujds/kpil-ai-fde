from typing import Literal, Optional

from dotenv import load_dotenv
from openai import OpenAI, pydantic_function_tool
from pydantic import BaseModel, Field, ValidationError

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"
MAX_ROUNDS = 3  # cap on model calls, so a stubborn model cannot loop forever

QUESTION = "Where is my order 4821?"


# 1. Structured input: the form the model fills in. One model does two jobs:
#    it describes the inputs to the model, and it checks what the model sends back.
class OrderLookup(BaseModel):
    """Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."""

    order_id: str = Field(pattern=r"^\d{4}$", description="The order number, four digits, for example 4821")


# 2. Structured tool result: every tool answers in the same labelled shape.
class OrderStatus(BaseModel):
    order_id: str
    status: Literal["packed", "shipped", "delivered"]
    note: str


class ToolResult(BaseModel):
    ok: bool
    data: Optional[OrderStatus] = None
    message: str = ""  # a readable hint when something goes wrong
    source: str = "order system"


# 3. Structured final answer: the contract for what the agent hands to the next system.
class OrderAnswer(BaseModel):
    order_id: Optional[str] = Field(description="The order number discussed, or null if there was none")
    status: Literal["packed", "shipped", "delivered", "not_found", "unknown"]
    needs_human: bool = Field(description="True if a person should follow up")
    reply: str = Field(description="A short, friendly reply to the customer")


# The tool: a plain function that takes a checked input and returns a checked result.
def get_order_status(lookup: OrderLookup) -> ToolResult:
    orders = {
        "4821": OrderStatus(order_id="4821", status="shipped", note="Arrives Thursday"),
        "4822": OrderStatus(order_id="4822", status="packed", note="Ships tomorrow"),
    }
    order = orders.get(lookup.order_id)
    if order is None:
        return ToolResult(ok=False, message=f"No order found with number {lookup.order_id}. Check the number and try again.")
    return ToolResult(ok=True, data=order)


# The tool list is generated from the input model, so the description and the check cannot disagree.
tools = [pydantic_function_tool(OrderLookup, name="get_order_status")]


def run_tool(arguments: str) -> ToolResult:
    # 4. Validate what the model sent before anything runs. Bad JSON and bad values both land here.
    try:
        lookup = OrderLookup.model_validate_json(arguments)
    except ValidationError as error:
        # Send the real error text back so the model can correct itself.
        return ToolResult(ok=False, message=f"Invalid input, please fix and call again: {error}")
    return get_order_status(lookup)


def ask_model(messages: list):
    # Passing response_format makes a direct (non-tool) answer arrive in the OrderAnswer shape.
    response = client.chat.completions.parse(model=MODEL, messages=messages, tools=tools, response_format=OrderAnswer)
    return response.choices[0].message


messages = [{"role": "user", "content": QUESTION}]
print("User:", QUESTION, "\n")

answer = None
for _ in range(MAX_ROUNDS):
    reply = ask_model(messages)

    if not reply.tool_calls:
        # 6. The model answered. Validation already happened inside parse().
        answer = reply.parsed
        break

    # The model did not answer. It asked us to run one or more tools.
    messages.append(reply)
    for call in reply.tool_calls:
        print(f"Model asks for: {call.function.name}({call.function.arguments})")

        result = run_tool(call.function.arguments)
        print("Tool returned:", result.model_dump_json(), "\n")

        # 5. Send the structured result back, tagged with the id of the request it answers.
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result.model_dump_json()})

if answer is None:
    print("Gave up: no valid answer after", MAX_ROUNDS, "rounds. Hand this one to a person.")
else:
    print("Structured answer:", answer.model_dump_json(indent=2))
    print("\nAI:", answer.reply)
