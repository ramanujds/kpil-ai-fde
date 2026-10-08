"""Settings and retriever setup shared by ask.py and compare_retrieval.py."""
import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
CHROMA_PATH = ".chroma"
COLLECTION = "multi_format_docs"
DOCSTORE_PATH = ".store/docstore.json"


def configure_models():
    # ingest.py and ask.py must use the same embedding model, so the choice lives here.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)
    # Only ask.py uses the chat model to answer. The fusion retriever below also wants an LLM
    # object to exist, though with num_queries=1 it never calls it.
    Settings.llm = OpenAI(model=CHAT_MODEL)


def open_index():
    collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection(COLLECTION)
    return VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))


def open_nodes():
    # The keyword retriever needs the node text. ingest.py saved a copy next to the Chroma data.
    return list(SimpleDocumentStore.from_persist_path(DOCSTORE_PATH).docs.values())


def build_retrievers(index, nodes, file_type=None, top_k=4):
    """Returns (vector, keyword, hybrid) retrievers, optionally limited to one file type."""
    filters = None
    if file_type:
        filters = MetadataFilters.from_dicts([{"key": "file_type", "value": file_type}])

    # Finds nodes whose meaning is close to the question.
    vector = index.as_retriever(similarity_top_k=top_k, filters=filters)
    # Finds nodes that share the exact words of the question, such as "L3" or "25,000".
    # BM25Retriever's own filters option did not restrict results when we tried it, so we
    # hand it only the nodes of the chosen file type.
    keyword_nodes = [n for n in nodes if not file_type or n.metadata["file_type"] == file_type]
    keyword = BM25Retriever.from_defaults(nodes=keyword_nodes, similarity_top_k=top_k)
    # Merges the two ranked lists. num_queries=1 means the question is not rewritten into
    # several variants, so no extra model call is made.
    hybrid = QueryFusionRetriever(
        [vector, keyword],
        similarity_top_k=top_k,
        num_queries=1,
        mode="reciprocal_rerank",
        use_async=False,
    )
    return vector, keyword, hybrid


def describe(node):
    """A short 'file > where' label for a source node."""
    meta = node.metadata
    kind = meta["file_type"]
    if kind == "pdf":
        where = f"page {meta['page']}"
    elif kind == "xlsx":
        where = f"sheet {meta['sheet']}, row {meta['row']}"
    elif kind == "csv":
        where = f"row {meta['row']}"
    else:
        where = node.text.splitlines()[0].lstrip("# ")
    return f"{meta['file_name']} > {where}"
