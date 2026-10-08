from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# Reads OPENAI_API_KEY from the .env file. ChatOpenAI picks it up automatically.
load_dotenv()

# CHANGED: one LangChain model object replaces the OpenAI client.
model = ChatOpenAI(model="gpt-4o-mini")

# A fake order table shared by all the tools.
orders = {
    "4821": "Shipped, arrives Thursday",
    "4822": "Packed, ships tomorrow",
}


# 1. The tools: plain Python functions. The model never runs these, our code does.
# CHANGED: the @tool line replaces the whole hand-written tool description.
# LangChain builds it from the function name, the type hints (order_id: str) and the
# docstring below. The docstring is what the model reads, so say when to use it.
@tool
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of an order. Use when the customer asks where their order is. Do not use for refunds."""
    return orders.get(order_id, f"No order found with number {order_id}. Check the number and try again.")


# 2. Give the tools to the model.
# CHANGED: bind_tools() replaces passing tools=tools on every call.
tools = [get_order_status]
model_with_tools = model.bind_tools(tools)

# Name -> tool lookup. The model answers with a tool name as text, so we use this
# dictionary to find the matching function instead of hardcoding one tool in the loop.
# Add a tool to the list above and it is picked up here automatically.
tools_by_name = {t.name: t for t in tools}

messages = [HumanMessage("Update the order 4821 to Delivered, arrives Thursday")]
print("User:", messages[0].content, "\n")

# 3. First call: the model sees the question and the tools.
# CHANGED: invoke() replaces client.chat.completions.create(...).
reply = model_with_tools.invoke(messages)

# CHANGED: tool_calls is already a list of dicts. No json.loads needed.
if reply.tool_calls:
    # The model did not answer. It asked us to run one or more tools.
    messages.append(reply)

    for call in reply.tool_calls:
        print(f"Model asks for: {call['name']}({call['args']})")

        # 4. Our code runs the real function, chosen by the name the model sent.
        # CHANGED: a tool made with @tool is run with .invoke(), passing the arguments dict.
        selected_tool = tools_by_name.get(call["name"])
        if selected_tool is None:
            # The model can ask for a name we never gave it. Tell it, don't crash.
            result = f"Unknown tool: {call['name']}"
        else:
            result = selected_tool.invoke(call["args"])
        print("Tool returned:", result, "\n")

        # 5. Send the result back, tagged with the id of the request it answers.
        # CHANGED: ToolMessage replaces {"role": "tool", "tool_call_id": ..., "content": ...}.
        messages.append(ToolMessage(str(result), tool_call_id=call["id"]))

    # 6. Second call: the model reads the result and writes the final answer.
    reply = model_with_tools.invoke(messages)

print("AI:", reply.content)
