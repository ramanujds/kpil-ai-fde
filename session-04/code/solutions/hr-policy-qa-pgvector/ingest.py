from pathlib import Path

import psycopg2
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding

from store import FULL_TABLE, get_connection, get_vector_store

# One setting chooses the embedding model for the whole app. ask.py must use the same one.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Step 1: load every file in docs/. We keep only the file name as metadata.
documents = SimpleDirectoryReader(
    "docs", file_metadata=lambda path: {"file_name": Path(path).name}
).load_data()

# Step 2: cut each document into nodes (LlamaIndex's word for chunks), one per heading.
nodes = MarkdownNodeParser().get_nodes_from_documents(documents)
print(f"Made {len(nodes)} nodes from {len(documents)} documents.")

# Start from an empty table so that running this twice does not store duplicates.
try:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {FULL_TABLE}")
except psycopg2.OperationalError as error:
    raise SystemExit(f"Cannot reach Postgres. Is the container running? Try: docker compose up -d --wait\n{error}")

# Steps 3 and 4: the index embeds every node and stores it in Postgres through pgvector.
storage_context = StorageContext.from_defaults(vector_store=get_vector_store())
VectorStoreIndex(nodes, storage_context=storage_context)

# Ask Postgres directly how many rows it holds. This is ordinary SQL.
with get_connection() as conn, conn.cursor() as cur:
    cur.execute(f"SELECT count(*) FROM {FULL_TABLE}")
    print(f"Stored {cur.fetchone()[0]} nodes in the {FULL_TABLE} table. Now run ask.py.")
