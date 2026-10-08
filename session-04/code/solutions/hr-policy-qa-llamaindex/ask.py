import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

# The same embedding model as ingest.py, plus the chat model.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = OpenAI(model="gpt-4o-mini")

SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)

# Open the Chroma collection that ingest.py filled, and wrap it as an index.
collection = chromadb.PersistentClient(path=".chroma").get_collection("policies_llamaindex")
index = VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))

# Steps 5 and 6 in one object. A chat engine in this mode:
#   - rewrites a follow-up ("And does it carry forward?") into a full question,
#   - retrieves the 4 closest nodes, dropping any below the similarity cut-off,
#   - sends the nodes and the question to the model, and remembers the conversation.
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    similarity_top_k=4,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.3)],
    system_prompt=SYSTEM,
)

print("Ask about company policies. Type 'reset' to forget the conversation, 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break
    if question.lower() == "reset":
        chat_engine.reset()
        print("Conversation cleared.\n")
        continue

    response = chat_engine.chat(question)

    print("AI:", response)
    print("Retrieved from:")
    if not response.source_nodes:
        print("  - nothing above the similarity cut-off")
    for node in response.source_nodes:
        heading = node.text.splitlines()[0].lstrip("# ")
        print(f"  - {node.metadata['file_name']} > {heading} (score {node.score:.2f})")
    print()
