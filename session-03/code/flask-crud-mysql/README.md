# Book Library API - Flask + MySQL (Docker)

The same CRUD API as `session-03/code/flask-crud/`, with one change: `store.py` reads and
writes a MySQL database instead of a Python dict, so data survives a restart. MySQL runs in
a Docker container; the Flask app runs on your machine.

## Prerequisites

- Docker Desktop running
- `uv`

## Setup

1. Copy the env file (the password is used by both Docker and the app):
   ```
   cp .env.example .env
   ```
2. Start MySQL and wait until it is healthy:
   ```
   docker compose up -d --wait
   ```
   The `book_library` database is created automatically on first start.
3. Install dependencies:
   ```
   uv sync
   ```
4. Start the server:
   ```
   uv run flask --app app run --debug
   ```
   On first run this creates the `books` table and seeds it with three books.

Try `http://127.0.0.1:5000/books`, add a book, restart the server, and the data is still there.

## Handy Docker commands

| Command | What it does |
|---|---|
| `docker compose logs -f mysql` | Watch the database logs |
| `docker compose exec mysql mysql -uroot -p book_library` | Open a SQL prompt |
| `docker compose down` | Stop MySQL, keep the data |
| `docker compose down -v` | Stop MySQL and delete the data |

## What Changed From flask-crud

| File | flask-crud | This version |
|---|---|---|
| `app.py` | Same routes | Same routes, plus `init_db()` at startup |
| `models.py` | Pydantic shapes | Unchanged |
| `store.py` | A dict in memory | SQL statements against MySQL |
| `database.py` | Did not exist | Connection settings and table setup |
| `docker-compose.yml` | Did not exist | Runs MySQL in a container |
