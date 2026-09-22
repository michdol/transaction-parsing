"""Small synchronous SQLite wrapper for storing/reopening imports.

Each call opens its own short-lived connection, which keeps this safe for a
single-process synchronous FastAPI app without worrying about shared
connection/thread issues.
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional


class Database:
    def __init__(self, path: str):
        self.path = path
        parent = Path(path).parent
        if str(parent) not in ("", "."):
            parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS imports (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    accepted_count INTEGER NOT NULL,
                    rejected_count INTEGER NOT NULL,
                    total_minor INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    accepted_json TEXT NOT NULL,
                    rejected_json TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def save_import(self, record: dict) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO imports (
                    id, created_at, accepted_count, rejected_count,
                    total_minor, currency, accepted_json, rejected_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record["created_at"],
                    record["accepted_count"],
                    record["rejected_count"],
                    record["total_minor"],
                    record["currency"],
                    json.dumps(record["accepted"]),
                    json.dumps(record["rejected"]),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_import(self, import_id: str) -> Optional[dict]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM imports WHERE id = ?", (import_id,)
            ).fetchone()
            return self._row_to_record(row) if row else None
        finally:
            conn.close()

    def list_imports(self) -> list:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM imports ORDER BY created_at DESC, rowid DESC"
            ).fetchall()
            return [self._row_to_record(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "accepted_count": row["accepted_count"],
            "rejected_count": row["rejected_count"],
            "total_minor": row["total_minor"],
            "currency": row["currency"],
            "accepted": json.loads(row["accepted_json"]),
            "rejected": json.loads(row["rejected_json"]),
        }
