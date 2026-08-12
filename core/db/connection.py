"""Conexão SQLite centralizada."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "aga_help.db"


def get_connection() -> sqlite3.Connection:
    """Abre conexão SQLite com PRAGMAs de segurança e performance."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
