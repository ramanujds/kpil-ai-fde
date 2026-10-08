from langchain_ollama import ChatOllama

# CHANGED: one LangChain model object replaces the OpenAI client and its base_url.
model = ChatOllama(model="llama3:8b")

print("Chat with llama3:8b using LangChain. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # CHANGED: invoke() takes the question directly, no role dictionary needed.
    # Only the current question is sent. The model remembers nothing.
    response = model.invoke(user_input)

    # CHANGED: the answer is simply response.content.
    print("AI:", response.content, "\n")
