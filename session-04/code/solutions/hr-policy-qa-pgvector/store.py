import os

import psycopg2
from dotenv import load_dotenv
from llama_index.vector_stores.postgres import PGVectorStore

# Reads the database settings (and OPENAI_API_KEY) from the .env file.
load_dotenv()

TABLE = "policies"
# LlamaIndex adds a "data_" prefix, so the nodes live in a table called data_policies.
FULL_TABLE = f"data_{TABLE}"


def connection_settings():
    return {
        "host": "localhost",
        "port": int(os.environ["POSTGRES_PORT"]),
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "dbname": os.environ["POSTGRES_DB"],
    }


def get_connection():
    """A plain Postgres connection, for the SQL we write ourselves."""
    return psycopg2.connect(**connection_settings())


def get_vector_store():
    """The LlamaIndex view of the same table. It creates the pgvector extension and the table if missing."""
    settings = connection_settings()
    return PGVectorStore.from_params(
        host=settings["host"],
        port=settings["port"],
        user=settings["user"],
        password=settings["password"],
        database=settings["dbname"],
        table_name=TABLE,
        embed_dim=1536,  # the size of a text-embedding-3-small vector
    )
