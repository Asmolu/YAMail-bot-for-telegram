import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

DB_PATH = Path(os.getenv("DATABASE_PATH", "users.db"))


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


@contextmanager
def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()