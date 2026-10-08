"""
Store: where the books live.

This is the "database" of the project, but it is only a Python dict held in
memory. That keeps the focus on the API itself. The consequences:
  - restart the server and every change is lost (seed data comes back)
  - the API code in main.py never touches the dict directly, it only calls
    the methods below, so this class could later be swapped for a real
    database without changing the routes.
"""

from models import Book, BookCreate, BookUpdate


class BookStore:
    def __init__(self):
        self._books: dict[int, Book] = {}  # id -> Book
        self._next_id = 1  # the id the next new book will get
        self._seed()

    def _seed(self):
        """Start with a few books so GET has something to return."""
        samples = [
            BookCreate(title="Wings of Fire", author="A. P. J. Abdul Kalam", year=1999),
            BookCreate(title="The Guide", author="R. K. Narayan", year=1958),
            BookCreate(title="Malgudi Days", author="R. K. Narayan", year=1943, available=False),
        ]
        for sample in samples:
            self.create(sample)

    # ---------------- Create ----------------
    def create(self, data: BookCreate) -> Book:
        # Build a Book: the client's data plus a server-chosen id.
        book = Book(id=self._next_id, **data.model_dump())
        self._books[book.id] = book
        self._next_id += 1
        return book

    # ---------------- Read ----------------
    def list(
        self,
        author: str | None = None,
        available: bool | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Book]:
        books = list(self._books.values())

        # Filters are optional: only apply the ones the client asked for.
        if author is not None:
            books = [b for b in books if author.lower() in b.author.lower()]
        if available is not None:
            books = [b for b in books if b.available == available]

        # Pagination: skip the first N, then take at most 'limit'.
        return books[skip : skip + limit]

    def get(self, book_id: int) -> Book | None:
        # dict.get returns None when the id does not exist (see 03_dicts.py).
        return self._books.get(book_id)

    # ---------------- Update ----------------
    def replace(self, book_id: int, data: BookCreate) -> Book | None:
        """PUT: swap the whole book. Every field comes from the client."""
        if book_id not in self._books:
            return None
        book = Book(id=book_id, **data.model_dump())
        self._books[book_id] = book
        return book

    def update(self, book_id: int, changes: BookUpdate) -> Book | None:
        """PATCH: change only the fields the client actually sent."""
        book = self._books.get(book_id)
        if book is None:
            return None
        # exclude_unset=True drops fields the client did not send at all,
        # so an omitted field is left alone (not overwritten with None).
        updated = book.model_copy(update=changes.model_dump(exclude_unset=True))
        self._books[book_id] = updated
        return updated

    # ---------------- Delete ----------------
    def delete(self, book_id: int) -> bool:
        # pop with a default returns None instead of raising KeyError.
        return self._books.pop(book_id, None) is not None
