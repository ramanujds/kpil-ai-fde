from collections import Counter

import chromadb
from dotenv import load_dotenv
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.chroma import ChromaVectorStore

from loaders import load_nodes
from retrieval import CHROMA_PATH, COLLECTION, DOCSTORE_PATH, configure_models

# Reads OPENAI_API_KEY from the .env file.
load_dotenv()
configure_models()

# Steps 1 and 2: read every file in docs/ and cut it into nodes. How it is cut depends on the
# file type. See loaders.py.
nodes = load_nodes("docs")

print("Nodes per file type:")
for file_type, count in sorted(Counter(node.metadata["file_type"] for node in nodes).items()):
    print(f"  {file_type:5} {count}")

# The keyword retriever in ask.py needs the node text, so we save a copy of the nodes.
docstore = SimpleDocumentStore()
docstore.add_documents(nodes)
docstore.persist(DOCSTORE_PATH)

# Steps 3 and 4: embed every node and store it in Chroma, with its metadata.
# We start from an empty collection so that running this twice does not store duplicates.
client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    client.delete_collection(COLLECTION)
except Exception:
    pass  # first run: there is nothing to delete yet
collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

storage_context = StorageContext.from_defaults(
    vector_store=ChromaVectorStore(chroma_collection=collection)
)
VectorStoreIndex(nodes, storage_context=storage_context)

print(f"Stored {collection.count()} nodes. Now run ask.py.")
