from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

# Step 1 and 2: load every document and cut it into chunks, one chunk per "## Section".
texts, metadatas = [], []
for path in sorted(Path("docs").glob("*.md")):
    header, *sections = path.read_text().split("\n## ")
    title = header.splitlines()[0].lstrip("# ")
    for section in sections:
        heading, body = section.split("\n", 1)
        # The title and heading go inside the chunk, so it makes sense on its own.
        texts.append(f"{title} > {heading}\n{body.strip()}")
        metadatas.append({"source": title, "section": heading})

print(f"Made {len(texts)} chunks from the documents.")

# Step 3: turn every chunk into a vector (a list of numbers that captures its meaning).
response = client.embeddings.create(model="text-embedding-3-small", input=texts)
vectors = [item.embedding for item in response.data]

# Step 4: store the vectors, with the original text and the source of each chunk.
collection = chromadb.PersistentClient(path=".chroma").get_or_create_collection(
    "policies", metadata={"hnsw:space": "cosine"}
)
collection.upsert(
    ids=[f"{m['source']} > {m['section']}" for m in metadatas],
    embeddings=vectors,
    documents=texts,
    metadatas=metadatas,
)

print(f"Stored {collection.count()} chunks. Now run ask.py.")
