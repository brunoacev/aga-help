"""Schema e migrações do banco SQLite."""

from __future__ import annotations

import sqlite3

from core.db.connection import get_connection
from core.db.orders_repository import backfill_order_timestamps


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
        for col in ["phone", "address", "width", "height", "items_json", "service_type", "payment_status", "billed_at"]:
            try:
                if col == "items_json":
                    default = "'[]'"
                elif col == "service_type":
                    default = "'componentes'"
                elif col == "payment_status":
                    default = "'Pendente'"
                else:
                    default = "''"
                conn.execute(f"ALTER TABLE orders ADD COLUMN {col} TEXT DEFAULT {default}")
            except sqlite3.OperationalError:
                pass
        try:
            conn.execute("ALTER TABLE orders ADD COLUMN is_billed INTEGER NOT NULL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE orders ADD COLUMN created_by TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                handle TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS order_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                user_handle TEXT NOT NULL,
                action_description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                synced INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        backfill_order_timestamps()
        migrate_kanban_statuses(conn)
        conn.commit()


def migrate_kanban_statuses(conn) -> None:
    """Converte status legados para PRODUCAO | PRONTO | FATURADO."""
    from core.kanban_stages import STAGE_FATURADO, STAGE_PRODUCAO, STAGE_PRONTO

    replacements = (
        ("Orçamento", STAGE_PRODUCAO),
        ("Orcamento", STAGE_PRODUCAO),
        ("Produção", STAGE_PRODUCAO),
        ("Producao", STAGE_PRODUCAO),
        ("Pronto", STAGE_PRONTO),
        ("Faturado", STAGE_FATURADO),
    )
    for old_status, new_status in replacements:
        conn.execute(
            "UPDATE orders SET status = ? WHERE status = ?",
            (new_status, old_status),
        )
