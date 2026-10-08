from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(model="llama3.1:8b", base_url="http://localhost:11434/v1",
    api_key="ollama")

# A fake order table used by the tools.
orders = {
    "4821": "Shipped, arrives Thursday",
    "4822": "Packed, ships tomorrow",
}


@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of an order. Use when the customer asks where their order is."""
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


@tool
def cancel_order(order_id: str) -> str:
    """Cancel an order. Use only when the customer clearly asks to cancel an order."""
    if order_id not in orders:
        return f"No order found with number {order_id}. Check the number and try again."
    orders[order_id] = "Cancelled"
    return f"Order {order_id} has been cancelled."


tools = [get_order_status, cancel_order]
model_with_tools = model.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}

# Tools that change something need a human to say yes before they run.
NEEDS_APPROVAL = {"cancel_order"}

history = [
    SystemMessage(
        "You are a helpful assistant. Use a tool only when one clearly matches the request. "
        "For general questions, or requests no tool can do, answer directly in plain text "
        "from your own knowledge, or say politely what you cannot do. "
        "Never mention functions or tools to the user. "
        "If a request is denied by the user, accept it and do not ask again."
    ),
]


def approved_by_human(name, args):
    answer = input(f"  Approval needed: {name}({args}). Allow? (y/n): ").strip().lower()
    return answer in ("y", "yes")


print("Chat started. Type 'exit' to quit.\n")

while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit"):
        break

    history.append(HumanMessage(user_input))
    reply = model_with_tools.invoke(history)

    while reply.tool_calls:
        history.append(reply)

        for call in reply.tool_calls:
            print(f"  [Model asks for: {call['name']}({call['args']})]")

            selected_tool = tools_by_name.get(call["name"])
            if selected_tool is None:
                result = f"Unknown tool: {call['name']}"
            elif call["name"] in NEEDS_APPROVAL and not approved_by_human(call["name"], call["args"]):
                # The tool never runs. The model is told, so it can explain to the user.
                result = "The user denied this action. It was not carried out."
            else:
                result = selected_tool.invoke(call["args"])
            print(f"  [Tool returned: {result}]")

            history.append(ToolMessage(str(result), tool_call_id=call["id"]))

        reply = model_with_tools.invoke(history)

    history.append(reply)
    print("AI:", reply.content, "\n")
