# HR Policy Q&A with LlamaIndex and pgvector

The LlamaIndex version of the HR policy assistant, with one change: the vectors are stored in **Postgres with the pgvector extension** instead of a local Chroma folder. Postgres runs in a Docker container.

The documents in `docs/` are synthetic, copied from the other versions of this app. "Acme" is a made-up company.

## Prerequisites

1. **uv**, the Python package manager.
2. **Docker** with Docker Compose, used only to run the database.
3. An OpenAI API key.

## Files

| File | What it does |
|---|---|
| `docker-compose.yml` | Starts Postgres 17 with pgvector already installed. Data is kept in a Docker volume. The port is open on localhost only. |
| `store.py` | Database settings read from `.env`, plus two helpers: a plain Postgres connection, and the LlamaIndex vector store on the same table. |
| `ingest.py` | Run once. Loads the documents, cuts them into nodes, embeds them, and stores them in the `data_policies` table. |
| `ask.py` | Run for every question. Same chat engine as the Chroma version: rewrites follow-ups, retrieves, answers, prints sources with scores. |
| `docs/` | Six policies: HR handbook, leave, laptop, work from home, expense reimbursement, IT security. |
| `.env.example` | Template for the key and the database settings. Copy it to `.env`. `.env` is ignored by Git. |

## Run

Copy `.env.example` to `.env` and put your real OpenAI key in it. The database settings can stay as they are. Then:

```
docker compose up -d --wait
uv sync
uv run ingest.py
uv run ask.py
```

`--wait` returns once Postgres is healthy. Run `ingest.py` again only when you change the documents. It rebuilds the table from scratch each time.

## Look Inside the Database

The vectors are now in a real database table, so you can read them with SQL.

Count the stored nodes:

```
docker compose exec db psql -U postgres -d hrpolicy -c "SELECT count(*) FROM data_policies"
```

See each node's file and the start of its text:

```
docker compose exec db psql -U postgres -d hrpolicy -c "SELECT metadata_->>'file_name' AS file, left(text, 50) AS start FROM data_policies"
```

The table has these columns: `id`, `text`, `metadata_`, `node_id` and `embedding`. The `embedding` column holds the vector, 1536 numbers per row.

## What Changed From the Chroma Version

| | Chroma version | pgvector version |
|---|---|---|
| Where vectors live | A `.chroma/` folder on disk | A table in Postgres |
| How you run it | Nothing to start | `docker compose up -d --wait` first |
| Search | Chroma's own query | A SQL query with pgvector's distance operator, run by LlamaIndex |
| Other data | A separate system | Can sit next to the vectors in the same database and be joined with SQL |
| Fits when | Learning, small local apps | A team that already runs Postgres, or needs backups, access control and filters by SQL |

The loading, chunking, chat engine and prompt are unchanged. Only the vector store behind the index was swapped, which is what LlamaIndex is for.

## Stop and Clean Up

```
docker compose down        # stop the database, keep the data
docker compose down -v     # stop the database and delete the data
```

## Notes

- The default `.env` values are for a throwaway local database holding only synthetic data. Do not reuse them anywhere real.
- The host port is 5433, so it does not clash with a Postgres you may already run on 5432. Change `POSTGRES_PORT` in `.env` if 5433 is taken, then run `docker compose up -d --wait` again.
- With six policies, a plain scan finds the closest vectors instantly. For a large collection, add an HNSW index (the `hnsw_kwargs` option of the LlamaIndex Postgres store) so searches stay fast.
- If `ingest.py` says it cannot reach Postgres, the container is not running. Start it with `docker compose up -d --wait` and check `docker compose ps`.
- The embedding model in `ask.py` must match `ingest.py`, and the table's vector size (1536) must match that model. Changing models means changing the size in `store.py` and re-running `ingest.py`.
