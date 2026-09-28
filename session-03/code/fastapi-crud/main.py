"""
Book Library API: a small CRUD REST API built with FastAPI.

CRUD maps onto HTTP methods:
    Create -> POST    /books
    Read   -> GET     /books         (list)   and   GET /books/{id}   (one)
    Update -> PUT     /books/{id}    (replace everything)
              PATCH   /books/{id}    (change some fields)
    Delete -> DELETE  /books/{id}

Run (from this folder):
    uv sync                    install the dependencies (first time only)
    uv run fastapi dev         start the server with auto-reload

Then open:
    http://127.0.0.1:8000/docs       Swagger UI  (try every endpoint in the browser)
    http://127.0.0.1:8000/redoc      ReDoc       (read-only documentation)
    http://127.0.0.1:8000/openapi.json   the machine-readable API description
"""

from fastapi import FastAPI, HTTPException, Query, status

from models import Book, BookCreate, BookUpdate
from store import BookStore

# ---------------------------------------------------------------
# The app object
# ---------------------------------------------------------------
# title, description and version appear at the top of the Swagger page.
# Every route is registered on this 'app' object with a decorator.
app = FastAPI(
    title="Book Library API",
    description="A small CRUD API. Data is kept in memory, so it resets when the server restarts.",
    version="1.0.0",
)

# One shared store for the whole app.
store = BookStore()

# Reused in several routes: how to describe a 404 in the docs.
NOT_FOUND = {404: {"description": "Book not found"}}


def get_book_or_404(book_id: int) -> Book:
    """Fetch a book or stop the request with a 404 error."""
    book = store.get(book_id)
    if book is None:
        # HTTPException turns into a JSON error: {"detail": "..."}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book {book_id} not found")
    return book


# ---------------------------------------------------------------
# Health check
# ---------------------------------------------------------------
@app.get("/health", tags=["System"], summary="Is the server up?")
def health():
    # A returned dict becomes JSON automatically.
    return {"status": "ok"}


# ---------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------
# response_model=Book  -> the response is shaped (and documented) as a Book.
# status_code=201      -> "Created", the right code when a new thing is made.
# 'book: BookCreate' is the request body; FastAPI reads the JSON and
# validates it against the model before this function even runs.
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
# Parameters that are NOT in the URL path become QUERY parameters:
#   GET /books?author=narayan&available=true&skip=0&limit=5
# Query(...) adds rules and descriptions that show up in Swagger.
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
# {book_id} in the path is a PATH parameter. The 'int' type hint makes
# FastAPI convert it, and reject /books/abc with a 422 error.
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
# PUT means "replace the whole thing", so the client sends every field.
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
# PATCH means "change only these fields". BookUpdate makes every field optional.
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
# 204 "No Content": success, and there is nothing to send back.
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
