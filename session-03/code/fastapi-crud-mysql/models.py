"""
Models: the SHAPE of the data our API accepts and returns.

Identical to the in-memory version's models.py. Pydantic models describe
the request and response bodies; they know nothing about MySQL, and don't
need to - that separation is what let the storage swap to a real database
without touching these classes.
"""

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    """What a client sends to CREATE (or fully REPLACE) a book."""

    title: str = Field(min_length=1, max_length=100, examples=["Wings of Fire"])
    author: str = Field(min_length=1, max_length=60, examples=["A. P. J. Abdul Kalam"])
    year: int = Field(ge=1000, le=2100, examples=[1999])
    available: bool = True


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

    The client never chooses the id; the database does (AUTO_INCREMENT).
    """

    id: int
