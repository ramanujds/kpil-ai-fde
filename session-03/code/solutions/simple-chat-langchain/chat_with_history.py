from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama

model = ChatOllama(model="llama3:8b")

# The chat history. It lives outside the loop, so it keeps growing.
messages = []

print("Chat with llama3:8b using LangChain. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # CHANGED: HumanMessage and AIMessage objects replace {"role": ..., "content": ...}.
    messages.append(HumanMessage(user_input))

    # Send the whole history, not just the latest question.
    response = model.invoke(messages)

    messages.append(AIMessage(response.content))

    print("AI:", response.content, "\n")
