"""
Book Library API: a small CRUD REST API built with FastAPI, backed by MySQL.

Same seven routes as the in-memory version (see session-03/code/fastapi-crud/),
but every change is now written to a real MySQL database, so the data
survives a server restart.

Setup (from this folder):
    Create the database once:   mysql -u root -p -e "CREATE DATABASE book_library"
    Copy the env file:          cp .env.example .env      (edit if your MySQL user/password differ)
    uv sync                     install the dependencies (first time only)
    uv run fastapi dev          start the server; creates and seeds the table on first run

Then open:
    http://127.0.0.1:8000/docs       Swagger UI  (try every endpoint in the browser)
    http://127.0.0.1:8000/redoc      ReDoc       (read-only documentation)
    http://127.0.0.1:8000/openapi.json   the machine-readable API description
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, status

from database import init_db
from models import Book, BookCreate, BookUpdate
from store import BookStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once, right before the app starts serving requests: make sure
    # the table exists and has seed data, so GET has something to return.
    init_db()
    yield


app = FastAPI(
    title="Book Library API (MySQL)",
    description="The same CRUD API as the in-memory version, now backed by a MySQL database.",
    version="1.0.0",
    lifespan=lifespan,
)

store = BookStore()

NOT_FOUND = {404: {"description": "Book not found"}}


def get_book_or_404(book_id: int) -> Book:
    """Fetch a book or stop the request with a 404 error."""
    book = store.get(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book {book_id} not found")
    return book


# ---------------------------------------------------------------
# Health check
# ---------------------------------------------------------------
@app.get("/health", tags=["System"], summary="Is the server up?")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------
@app.post(
    "/books",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
    summary="Add a new book",
)
def create_book(book: BookCreate):
    return store.create(book)


# ---------------------------------------------------------------
# READ (list)
# ---------------------------------------------------------------
@app.get(
    "/books",
    response_model=list[Book],
    tags=["Books"],
    summary="List books, with optional filters",
)
def list_books(
    author: str | None = Query(default=None, description="Part of the author's name"),
    available: bool | None = Query(default=None, description="Only available (true) or borrowed (false) books"),
    skip: int = Query(default=0, ge=0, description="How many books to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum books to return"),
):
    return store.list(author=author, available=available, skip=skip, limit=limit)


# ---------------------------------------------------------------
# READ (one)
# ---------------------------------------------------------------
@app.get(
    "/books/{book_id}",
    response_model=Book,
    responses=NOT_FOUND,
    tags=["Books"],
    summary="Get one book by id",
)
def get_book(book_id: int):
    return get_book_or_404(book_id)


# ---------------------------------------------------------------
# UPDATE (replace)
# ---------------------------------------------------------------
@app.put(
    "/books/{book_id}",
    response_model=Book,
    responses=NOT_FOUND,
    tags=["Books"],
    summary="Replace a book completely",
)
def replace_book(book_id: int, book: BookCreate):
    get_book_or_404(book_id)  # 404 if it does not exist
    return store.replace(book_id, book)


# ---------------------------------------------------------------
# UPDATE (partial)
# ---------------------------------------------------------------
@app.patch(
    "/books/{book_id}",
    response_model=Book,
    responses=NOT_FOUND,
    tags=["Books"],
    summary="Change some fields of a book",
)
def update_book(book_id: int, changes: BookUpdate):
    get_book_or_404(book_id)
    return store.update(book_id, changes)


# ---------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------
@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND,
    tags=["Books"],
    summary="Delete a book",
)
def delete_book(book_id: int):
    get_book_or_404(book_id)
    store.delete(book_id)
