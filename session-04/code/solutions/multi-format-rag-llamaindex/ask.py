from dotenv import load_dotenv
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer

from retrieval import build_retrievers, configure_models, describe, open_index, open_nodes

load_dotenv()
configure_models()

SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "The context can come from a handbook, a PDF policy, spreadsheet rows, a checklist or an FAQ. "
    "If the answer needs facts from more than one source, combine them. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)

index = open_index()
nodes = open_nodes()

# One memory object that outlives the engine, so changing the file type filter
# does not make the assistant forget the conversation.
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)


def make_engine(file_type):
    # Hybrid retrieval: vector search and keyword search, merged. See retrieval.py.
    _, _, hybrid = build_retrievers(index, nodes, file_type=file_type)
    return CondensePlusContextChatEngine.from_defaults(
        retriever=hybrid, memory=memory, system_prompt=SYSTEM
    )


file_type = None
chat_engine = make_engine(file_type)

print("Ask about company policies.")
print("Commands: /only pdf|xlsx|md|docx|csv  search one file type    /only all  search everything")
print("          reset  forget the conversation    quit  exit\n")

while True:
    question = input("You: ").strip()

    if question.lower() in ("quit", "exit"):
        break
    if question.lower() == "reset":
        memory.reset()
        print("Conversation cleared.\n")
        continue
    if question.lower().startswith("/only"):
        choice = question[5:].strip().lower()
        file_type = None if choice in ("", "all") else choice
        chat_engine = make_engine(file_type)
        print(f"Searching {file_type or 'all file types'}.\n")
        continue

    response = chat_engine.chat(question)

    print("AI:", response)
    print("Retrieved from:")
    if not response.source_nodes:
        print("  - nothing found")
    for node in response.source_nodes:
        print(f"  - {describe(node.node)} (score {node.score:.3f})")
    print()
