"""
Book Library API: a small CRUD REST API built with Flask.

Same API as flask-crud, but the books are stored in MySQL (running in Docker).

CRUD maps onto HTTP methods:
    Create -> POST    /books
    Read   -> GET     /books         (list)   and   GET /books/<id>   (one)
    Update -> PUT     /books/<id>    (replace everything)
              PATCH   /books/<id>    (change some fields)
    Delete -> DELETE  /books/<id>

Run (from this folder):
    docker compose up -d       start MySQL in a container
    uv sync                    install the dependencies (first time only)
    uv run flask --app app run --debug     start the server with auto-reload

Flask has no built-in Swagger page, so test with curl, Postman or a browser:
    http://127.0.0.1:5000/health
    http://127.0.0.1:5000/books
"""

from flask import Flask, jsonify, request
from pydantic import ValidationError

from database import init_db
from models import BookCreate, BookUpdate
from store import BookStore

# ---------------------------------------------------------------
# The app object
# ---------------------------------------------------------------
# Every route is registered on this 'app' object with a decorator.
app = Flask(__name__)

# One shared store for the whole app. Data lives in MySQL,
# so it survives a server restart.
store = BookStore()

# Runs once at startup: make sure the table exists and has seed data.
init_db()


# ---------------------------------------------------------------
# Errors
# ---------------------------------------------------------------
# Flask does not validate anything for us, so we turn problems into JSON
# errors ourselves. FastAPI did all of this automatically.
class BadRequest(Exception):
    """Raised when the request body is not a JSON object."""


def error(message, code):
    return jsonify({"detail": message}), code


@app.errorhandler(ValidationError)
def handle_validation_error(exc: ValidationError):
    # Raised by Pydantic when the JSON has a wrong type or a broken rule.
    # include_url=False keeps the messages short.
    return jsonify({"detail": exc.errors(include_url=False, include_context=False)}), 422


@app.errorhandler(404)
def handle_404(_):
    return error("Not found", 404)


@app.errorhandler(405)
def handle_405(_):
    return error("Method not allowed", 405)


def read_json_body() -> dict:
    """Return the request's JSON object, or raise a 400-style error."""
    # silent=True gives None instead of raising when the body is not valid JSON.
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise BadRequest("Request body must be a JSON object")
    return body


@app.errorhandler(BadRequest)
def handle_bad_request(exc: BadRequest):
    return error(str(exc), 400)


def book_not_found(book_id: int):
    return error(f"Book {book_id} not found", 404)


# ---------------------------------------------------------------
# Health check
# ---------------------------------------------------------------
@app.get("/health")
def health():
    # jsonify turns a dict into a JSON response.
    return jsonify({"status": "ok"})


# ---------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------
# BookCreate(**body) validates the JSON: wrong type or missing field
# raises ValidationError, handled above as a 422.
# 201 = "Created", the right code when a new thing is made.
@app.post("/books")
def create_book():
    data = BookCreate(**read_json_body())
    book = store.create(data)
    return jsonify(book.model_dump()), 201


# ---------------------------------------------------------------
# READ (list)
# ---------------------------------------------------------------
# Query parameters come from request.args (always strings):
#   GET /books?author=narayan&available=true&skip=0&limit=5
@app.get("/books")
def list_books():
    author = request.args.get("author")

    # request.args.get(..., type=int) returns None when it is not a number.
    skip = request.args.get("skip", default=0, type=int)
    limit = request.args.get("limit", default=10, type=int)
    if skip is None or skip < 0:
        return error("skip must be an integer >= 0", 422)
    if limit is None or not 1 <= limit <= 100:
        return error("limit must be an integer between 1 and 100", 422)

    available = None
    if "available" in request.args:
        text = request.args["available"].lower()
        if text not in ("true", "false"):
            return error("available must be true or false", 422)
        available = text == "true"

    books = store.list(author=author, available=available, skip=skip, limit=limit)
    return jsonify([book.model_dump() for book in books])


# ---------------------------------------------------------------
# READ (one)
# ---------------------------------------------------------------
# <int:book_id> in the path is a PATH parameter. The 'int:' converter
# makes Flask convert it, and answer 404 for /books/abc.
@app.get("/books/<int:book_id>")
def get_book(book_id: int):
    book = store.get(book_id)
    if book is None:
        return book_not_found(book_id)
    return jsonify(book.model_dump())


# ---------------------------------------------------------------
# UPDATE (replace)
# ---------------------------------------------------------------
# PUT means "replace the whole thing", so the client sends every field.
@app.put("/books/<int:book_id>")
def replace_book(book_id: int):
    if store.get(book_id) is None:
        return book_not_found(book_id)
    data = BookCreate(**read_json_body())
    return jsonify(store.replace(book_id, data).model_dump())


# ---------------------------------------------------------------
# UPDATE (partial)
# ---------------------------------------------------------------
# PATCH means "change only these fields". BookUpdate makes every field optional.
@app.patch("/books/<int:book_id>")
def update_book(book_id: int):
    if store.get(book_id) is None:
        return book_not_found(book_id)
    changes = BookUpdate(**read_json_body())
    return jsonify(store.update(book_id, changes).model_dump())


# ---------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------
# 204 "No Content": success, and there is nothing to send back.
@app.delete("/books/<int:book_id>")
def delete_book(book_id: int):
    if store.get(book_id) is None:
        return book_not_found(book_id)
    store.delete(book_id)
    return "", 204
