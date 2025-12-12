import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/users.db"))


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                token TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_user_token(user_id: int, token: str) -> None:
    with _get_connection() as conn:
        conn.execute(
            "REPLACE INTO users (user_id, token) VALUES (?, ?)",
            (user_id, token),
        )


def get_user_token(user_id: int) -> Optional[str]:
    with _get_connection() as conn:
        cursor = conn.execute(
            "SELECT token FROM users WHERE user_id = ?", (user_id,)
        )
        row = cursor.fetchone()
    return row[0] if row else None


def delete_user_token(user_id: int) -> None:
    with _get_connection() as conn:
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))


def save_uploaded_file(user_id: int, file_name: str) -> None:
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO file_history (user_id, file_name) VALUES (?, ?)",
            (user_id, file_name),
        )


def get_recent_files(user_id: int, limit: int = 5):
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT file_name, uploaded_at
            FROM file_history
            WHERE user_id = ?
            ORDER BY uploaded_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return cursor.fetchall()


@contextmanager
def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()