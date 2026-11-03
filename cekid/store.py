"""Penyimpanan chat yang pernah dilihat bot (SQLite, bukan JSON)."""

import sqlite3
import time


class Store:
    def __init__(self, path: str) -> None:
        self.path = path
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id   INTEGER PRIMARY KEY,
                    title     TEXT,
                    type      TEXT,
                    username  TEXT,
                    seen_at   INTEGER
                )
                """
            )

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def save_chat(self, chat) -> None:
        if chat is None:
            return
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO chats (chat_id, title, type, username, seen_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    title=excluded.title,
                    type=excluded.type,
                    username=excluded.username,
                    seen_at=excluded.seen_at
                """,
                (
                    chat.id,
                    getattr(chat, "title", None),
                    str(getattr(chat, "type", "")),
                    getattr(chat, "username", None),
                    int(time.time()),
                ),
            )

    def chats(self, kinds: list[str], limit: int = 50) -> list[sqlite3.Row]:
        """Ambil chat berdasarkan tipe: ["ChatType.GROUP", "ChatType.SUPERGROUP"]."""
        placeholders = ",".join("?" for _ in kinds)
        with self._conn() as conn:
            return conn.execute(
                f"SELECT * FROM chats WHERE type IN ({placeholders}) "
                "ORDER BY seen_at DESC LIMIT ?",
                (*kinds, limit),
            ).fetchall()
