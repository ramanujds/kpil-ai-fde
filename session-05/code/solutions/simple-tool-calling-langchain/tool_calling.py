from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(model="docker.io/ai/gemma4:E4B", base_url="http://localhost:12434/v1",
    api_key="ollama")

# A fake order table used by the tool.
orders = {
    "4821": "Shipped, arrives Thursday",
    "4822": "Packed, ships tomorrow",
}


# The model never runs this, our code does. LangChain builds the tool description
# from the name, the type hints and the docstring, so the docstring says when to use it.
@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."""
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


tools = [get_order_status]
model_with_tools = model.bind_tools(tools)

# Name -> tool lookup, so the loop works for any tool added to the list above.
tools_by_name = {t.name: t for t in tools}

# The full history is sent on every call, so the model remembers earlier turns.
# The system message tells it to answer directly when no tool fits.
history = [
    SystemMessage(
        "You are a helpful assistant. Use a tool only when one clearly matches the request. "
        "For general questions, or requests no tool can do, answer directly in plain text "
        "from your own knowledge, or say politely what you cannot do. "
        "Never mention functions or tools to the user."
    ),
]

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

    # While the model asks for tools, run them and send the results back.
    while reply.tool_calls:
        history.append(reply)

        for call in reply.tool_calls:
            print(f"  [Model asks for: {call['name']}({call['args']})]")

            selected_tool = tools_by_name.get(call["name"])
            if selected_tool is None:
                # The model can ask for a name we never gave it. Tell it, don't crash.
                result = f"Unknown tool: {call['name']}"
            else:
                result = selected_tool.invoke(call["args"])
            print(f"  [Tool returned: {result}]")

            history.append(ToolMessage(str(result), tool_call_id=call["id"]))

        reply = model_with_tools.invoke(history)

    history.append(reply)
    print("AI:", reply.content, "\n")
