"""
Store: where the books live.

Same class name and same six methods as the in-memory version's store.py -
create, list, get, replace, update, delete - but every one now runs a SQL
statement against MySQL instead of touching a dict. app.py never changed
at all: it only ever called these methods, never the dict or the database
directly, so the swap is contained entirely to this file (plus database.py).
"""

from database import get_connection
from models import Book, BookCreate, BookUpdate


def _row_to_book(row: tuple) -> Book:
    id_, title, author, year, available = row
    return Book(id=id_, title=title, author=author, year=year, available=bool(available))


class BookStore:
    # ---------------- Create ----------------
    def create(self, data: BookCreate) -> Book:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, year, available) VALUES (%s, %s, %s, %s)",
                (data.title, data.author, data.year, data.available),
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
        finally:
            conn.close()
        return Book(id=new_id, **data.model_dump())

    # ---------------- Read ----------------
    def list(
        self,
        author: str | None = None,
        available: bool | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Book]:
        # Build the WHERE clause only from filters the client actually asked
        # for. '%s' placeholders keep every value parameterized, never
        # pasted into the SQL text, which is what avoids SQL injection.
        query = "SELECT id, title, author, year, available FROM books WHERE 1=1"
        params: list = []
        if author is not None:
            query += " AND author LIKE %s"
            params.append(f"%{author}%")
        if available is not None:
            query += " AND available = %s"
            params.append(available)
        query += " ORDER BY id LIMIT %s OFFSET %s"
        params += [limit, skip]

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
        finally:
            conn.close()
        return [_row_to_book(row) for row in rows]

    def get(self, book_id: int) -> Book | None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, author, year, available FROM books WHERE id = %s",
                (book_id,),
            )
            row = cursor.fetchone()
            cursor.close()
        finally:
            conn.close()
        return _row_to_book(row) if row else None

    # ---------------- Update ----------------
    def replace(self, book_id: int, data: BookCreate) -> Book | None:
        """PUT: swap the whole book. Every field comes from the client."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE books SET title=%s, author=%s, year=%s, available=%s WHERE id=%s",
                (data.title, data.author, data.year, data.available, book_id),
            )
            found = cursor.rowcount > 0
            conn.commit()
            cursor.close()
        finally:
            conn.close()
        return Book(id=book_id, **data.model_dump()) if found else None

    def update(self, book_id: int, changes: BookUpdate) -> Book | None:
        """PATCH: change only the fields the client actually sent.

        model_dump(exclude_unset=True) drops fields the client never sent,
        so only those columns appear in the SQL SET clause; the rest are
        left exactly as they were in the row.
        """
        fields = changes.model_dump(exclude_unset=True)
        if not fields:
            return self.get(book_id)

        # Column names come from the model's own fields, not from client
        # input, so building the SET clause this way is still safe - only
        # the values are placeholders.
        set_clause = ", ".join(f"{column}=%s" for column in fields)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE books SET {set_clause} WHERE id=%s",
                (*fields.values(), book_id),
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()
        return self.get(book_id)

    # ---------------- Delete ----------------
    def delete(self, book_id: int) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            cursor.close()
        finally:
            conn.close()
        return deleted
