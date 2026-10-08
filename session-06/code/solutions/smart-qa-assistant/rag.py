"""Retrieval: find the passages in the Chroma collection that best match a question."""

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

import config

_retriever = None


def _get_retriever():
    """Open the Chroma collection that ingest.py filled, the first time it is needed."""
    global _retriever
    if _retriever is None:
        collection = chromadb.PersistentClient(path=config.CHROMA_PATH).get_collection(config.COLLECTION)
        index = VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))
        _retriever = index.as_retriever(similarity_top_k=config.TOP_K)
    return _retriever


def reset() -> None:
    """Forget the open collection. Call after ingest.py rebuilds it, so the next search reopens it."""
    global _retriever
    _retriever = None


def search(question: str) -> list[dict]:
    """Return the matching passages as {source, text, score}, best first.

    Weak matches are dropped. An empty list means "the documents do not cover this".
    """
    passages = []
    for hit in _get_retriever().retrieve(question):
        if hit.score is None or hit.score < config.MIN_SCORE:
            continue
        heading = hit.node.get_content().splitlines()[0].lstrip("# ")
        passages.append(
            {
                "source": f"{hit.node.metadata['file_name']} > {heading}",
                "text": hit.node.get_content(),
                "score": hit.score,
            }
        )
    return passages
