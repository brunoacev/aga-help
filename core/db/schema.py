"""Schema e migrações do banco SQLite."""

from __future__ import annotations

import sqlite3

from core.db.connection import get_connection


def init_db() -> None:
    """Inicializa tabelas de pedidos, contatos e logs."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                reseller_name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                address TEXT DEFAULT '',
                value REAL NOT NULL,
                entry_date TEXT NOT NULL,
                deadline_date TEXT NOT NULL,
                description TEXT NOT NULL,
                width TEXT DEFAULT '',
                height TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Orçamento',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                address TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        for col in ["phone", "address", "width", "height"]:
            try:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
        conn.commit()
