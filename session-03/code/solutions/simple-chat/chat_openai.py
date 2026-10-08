from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"

print("Chat with OpenAI's gpt-4o-mini. Type 'quit' to exit.\n")

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
