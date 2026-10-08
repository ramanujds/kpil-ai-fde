"""
Models: the SHAPE of the data our API accepts and returns.

These are Pydantic models. FastAPI uses them to:
  1. validate incoming JSON (wrong type or missing field -> automatic 422 error)
  2. convert Python objects back to JSON in responses
  3. build the documentation you see in Swagger (/docs)
"""

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    """What a client sends to CREATE (or fully REPLACE) a book."""

    # Field(...) adds rules. min_length=1 means "not empty".
    # 'examples' is what Swagger pre-fills in the "Try it out" box.
    title: str = Field(min_length=1, max_length=100, examples=["Wings of Fire"])
    author: str = Field(min_length=1, max_length=60, examples=["A. P. J. Abdul Kalam"])
    year: int = Field(ge=1000, le=2100, examples=[1999])  # ge = greater or equal
    available: bool = True  # a default makes the field optional


class BookUpdate(BaseModel):
    """What a client sends to PARTIALLY update a book.

    Every field is optional (None by default): send only what changed.
    """

    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=60)
    year: int | None = Field(default=None, ge=1000, le=2100)
    available: bool | None = None


class Book(BookCreate):
    """What the API sends BACK: everything in BookCreate, plus the id.

    The client never chooses the id; the server does.
    """

    id: int
