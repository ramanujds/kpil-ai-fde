from pathlib import Path

import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# Reads OPENAI_API_KEY from the .env file.
load_dotenv()

# One setting chooses the embedding model for the whole app. ask.py must use the same one.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Step 1: load every file in docs/. With the llama-index-readers-file package added, it also reads PDF and Word.
# We keep only the file name as metadata. The default also holds the full file path, which would get embedded.
documents = SimpleDirectoryReader(
    "docs", file_metadata=lambda path: {"file_name": Path(path).name}
).load_data()

# Step 2: cut each document into nodes (LlamaIndex's word for chunks), one per heading.
nodes = MarkdownNodeParser().get_nodes_from_documents(documents)
print(f"Made {len(nodes)} nodes from {len(documents)} documents.")

# Steps 3 and 4: the index embeds every node and stores it in Chroma.
# We start from an empty collection so that running this twice does not store duplicates.
client = chromadb.PersistentClient(path=".chroma")
try:
    client.delete_collection("policies_llamaindex")
except Exception:
    pass  # first run: there is nothing to delete yet
collection = client.create_collection("policies_llamaindex", metadata={"hnsw:space": "cosine"})

storage_context = StorageContext.from_defaults(
    vector_store=ChromaVectorStore(chroma_collection=collection)
)
VectorStoreIndex(nodes, storage_context=storage_context)

print(f"Stored {collection.count()} nodes. Now run ask.py.")
