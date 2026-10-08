from openai import OpenAI

# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"

print("Chat with llama3:8b. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # Only the current question is sent. The model remembers nothing.
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
    )

    print("AI:", response.choices[0].message.content, "\n")
