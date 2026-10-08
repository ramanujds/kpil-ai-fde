"""Document ingestion: read everything in docs/, cut it into nodes, embed it, store it in Chroma.

Run this once, and again whenever a file in docs/ is added or changed. The browser UI calls
build_index() too, from its Re-index button.
"""

from pathlib import Path

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.vector_stores.chroma import ChromaVectorStore

import config


def build_index() -> tuple[int, int]:
    """Rebuild the Chroma collection from docs/. Returns (documents, nodes)."""
    # Step 1: load every file in docs/. Keep only the file name as metadata.
    documents = SimpleDirectoryReader(
        "docs", file_metadata=lambda path: {"file_name": Path(path).name}
    ).load_data()

    # Step 2: cut each document into nodes (LlamaIndex's word for chunks), one per heading.
    nodes = MarkdownNodeParser().get_nodes_from_documents(documents)

    # Steps 3 and 4: embed every node and store the vectors in Chroma. We start from an empty
    # collection so that running this twice does not store duplicates, and an updated policy
    # replaces the old version cleanly. "cosine" makes the score a similarity from 0 to 1.
    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    try:
        client.delete_collection(config.COLLECTION)
    except Exception:
        pass  # first run: there is nothing to delete yet
    collection = client.create_collection(config.COLLECTION, metadata={"hnsw:space": "cosine"})

    storage_context = StorageContext.from_defaults(
        vector_store=ChromaVectorStore(chroma_collection=collection)
    )
    VectorStoreIndex(nodes, storage_context=storage_context)
    return len(documents), collection.count()


if __name__ == "__main__":
    document_count, node_count = build_index()
    print(f"Made {node_count} nodes from {document_count} documents and stored them in Chroma. Now run app.py or ui.py.")
