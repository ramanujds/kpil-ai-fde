from openai import OpenAI

# Ollama runs on your machine and speaks the same API as OpenAI.
# The api_key is required by the library but Ollama ignores it.
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

MODEL = "llama3:8b"

# The chat history. It lives outside the loop, so it keeps growing.
messages = []

print("Chat with llama3:8b. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # Add the user's question to the history.
    messages.append({"role": "user", "content": user_input})

    # Send the whole history, not just the latest question.
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    answer = response.choices[0].message.content

    # Add the model's answer to the history too.
    messages.append({"role": "assistant", "content": answer})

    print("AI:", answer, "\n")
