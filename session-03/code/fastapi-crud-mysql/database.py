"""
Database: how the store talks to MySQL.

Plain mysql-connector-python, no ORM, so every SQL statement in store.py is
visible as written. Connection settings come from environment variables,
read once with python-dotenv, so no password ever appears in the code.
"""

import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector.connection import MySQLConnection

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "book_library")


def get_connection() -> MySQLConnection:
    """Open a fresh connection. The store opens and closes one per request,
    which is simple and fast enough for a small teaching app like this."""
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def init_db() -> None:
    """Create the books table if it does not exist yet, then seed it once.

    The database itself (book_library) must already exist - create it
    manually first, see the README. Creating a table is safe to repeat
    (IF NOT EXISTS), so this can run every time the app starts.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                author VARCHAR(60) NOT NULL,
                year INT NOT NULL,
                available BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )
        cursor.execute("SELECT COUNT(*) FROM books")
        (count,) = cursor.fetchone()
        if count == 0:
            cursor.executemany(
                "INSERT INTO books (title, author, year, available) VALUES (%s, %s, %s, %s)",
                [
                    ("Wings of Fire", "A. P. J. Abdul Kalam", 1999, True),
                    ("The Guide", "R. K. Narayan", 1958, True),
                    ("Malgudi Days", "R. K. Narayan", 1943, False),
                ],
            )
        conn.commit()
        cursor.close()
    finally:
        conn.close()
