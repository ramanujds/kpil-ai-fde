from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Reads OPENAI_API_KEY from the .env file. ChatOpenAI picks it up automatically.
load_dotenv()

# CHANGED: this is the ONLY line that differs from chat.py (plus the import above).
# The loop below is identical, which is the point of LangChain.
model = ChatOpenAI(model="gpt-4o-mini")

print("Chat with OpenAI's gpt-4o-mini using LangChain. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ("quit", "exit"):
        break

    # Only the current question is sent. The model remembers nothing.
    response = model.invoke(user_input)

    print("AI:", response.content, "\n")
