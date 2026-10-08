import ollama

MODEL = "llama3:8b"

print("Chat with llama3:8b using the Ollama library. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # Only the current question is sent. The model remembers nothing.
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
    )

    print("AI:", response.message.content, "\n")
