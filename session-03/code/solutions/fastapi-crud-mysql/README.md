# Book Library API - MySQL Version

The same CRUD API as `session-03/code/solutions/fastapi-crud/`, with one change: `store.py` now
reads and writes a MySQL database instead of a Python dict, so data survives a restart.
`main.py` and `models.py` are unchanged.

## Prerequisites

- MySQL server installed and running locally
- The `mysql` CLI available on your PATH

## Setup

1. Create the database once:
   ```
   mysql -u root -p -e "CREATE DATABASE book_library"
   ```
2. Copy the env file and adjust it if your MySQL user or password differ:
   ```
   cp .env.example .env
   ```
3. Install dependencies:
   ```
   uv sync
   ```
4. Start the server:
   ```
   uv run fastapi dev
   ```
   On first run this creates the `books` table and seeds it with three books.

Open `http://127.0.0.1:8000/docs` and try the same requests as the in-memory version -
then restart the server and see the data is still there.

## What Changed From the In-Memory Version

| File | In-memory version | This version |
|---|---|---|
| `main.py` | Same routes | Same routes, plus a startup step that prepares the table |
| `models.py` | Pydantic request/response shapes | Unchanged |
| `store.py` | A dict, held in memory | SQL statements against MySQL |
| `database.py` | Did not exist | Connection settings and table setup |

The routes in `main.py` never changed because they only ever called `store.create`,
`store.list`, `store.get`, `store.replace`, `store.update` and `store.delete` - never a
dict or a database directly.
