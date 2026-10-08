import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

collection = chromadb.PersistentClient(path=".chroma").get_collection("policies")

SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)

print("Ask about company policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    # Step 5: turn the question into a vector (same model as ingest.py), then
    # fetch the 4 stored chunks whose vectors are closest to it.
    response = client.embeddings.create(model="text-embedding-3-small", input=question)
    result = collection.query(query_embeddings=[response.data[0].embedding], n_results=4)
    chunks = result["documents"][0]

    # Step 6: send the chunks and the question to the model in one prompt.
    context = "\n\n".join(chunks)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )

    print("AI:", response.choices[0].message.content)
    print("Retrieved from:")
    for meta in result["metadatas"][0]:
        print(f"  - {meta['source']} > {meta['section']}")
    print()
