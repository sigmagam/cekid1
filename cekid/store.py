"""Penyimpanan user yang pernah /start (SQLite, bukan JSON)."""

import sqlite3
import time


class Store:
    def __init__(self, path: str) -> None:
        self.path = path
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id    INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name  TEXT,
                    username   TEXT,
                    started_at INTEGER
                )
                """
            )

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def save_user(self, user) -> None:
        if user is None or getattr(user, "is_bot", False):
            return
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO users (user_id, first_name, last_name, username, started_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    username=excluded.username
                """,
                (
                    user.id,
                    user.first_name,
                    getattr(user, "last_name", None),
                    getattr(user, "username", None),
                    int(time.time()),
                ),
            )

    def user_ids(self) -> list[int]:
        with self._conn() as conn:
            return [r["user_id"] for r in conn.execute("SELECT user_id FROM users")]

    def count(self) -> int:
        with self._conn() as conn:
            return conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
