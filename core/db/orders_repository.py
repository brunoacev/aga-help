"""Repositório de pedidos."""

from __future__ import annotations

from datetime import datetime

from core.constants import AGATEK_ADDRESS
from core.db.connection import get_connection
from core.db.logs_repository import add_log
from utils.sanitization import sanitize_name, sanitize_phone, sanitize_text


def add_order(
    order_number: str,
    reseller_name: str,
    phone: str,
    address: str,
    value: float,
    entry_date: str,
    deadline_date: str,
    description: str,
    width: str = "",
    height: str = "",
    status: str = "Orçamento",
    items_json: str = "[]",
    service_type: str = "componentes",
) -> None:
    """Insere um novo pedido."""
    target_address = sanitize_text(address) or AGATEK_ADDRESS
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO orders (
                order_number, reseller_name, phone, address, value,
                entry_date, deadline_date, description, width, height,
                status, created_at, items_json, service_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sanitize_text(order_number, max_length=30),
                sanitize_name(reseller_name),
                sanitize_phone(phone),
                target_address,
                value,
                sanitize_text(entry_date, max_length=20),
                sanitize_text(deadline_date, max_length=20),
                sanitize_text(description),
                sanitize_text(width, max_length=20),
                sanitize_text(height, max_length=20),
                sanitize_text(status, max_length=30),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                sanitize_text(items_json),
                sanitize_text(service_type, max_length=30),
            ),
        )
        conn.commit()
    add_log("NOVO PEDIDO", f"Pedido #{order_number} criado para {reseller_name}.")


def get_orders() -> list[dict]:
    """Retorna todos os pedidos ordenados por id decrescente."""
    with get_connection() as conn:
        conn.row_factory = _row_factory
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]


def update_order_status(order_id: int, new_status: str) -> None:
    """Atualiza o status de um pedido."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (sanitize_text(new_status, max_length=30), order_id),
        )
        conn.commit()


def delete_order(order_id: int) -> None:
    """Remove um pedido pelo id."""
    with get_connection() as conn:
        conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()


def clear_all_orders() -> None:
    """Remove todos os pedidos."""
    with get_connection() as conn:
        conn.execute("DELETE FROM orders")
        conn.commit()
    add_log("EXCLUSÃO", "Todos os pedidos do quadro Kanban foram limpos.")


def search_orders_by_reseller(query: str, limit: int = 3) -> list[dict]:
    """Busca revendas já cadastradas em pedidos."""
    clean_q = query.strip()
    if not clean_q or len(clean_q) < 2:
        return []
    with get_connection() as conn:
        conn.row_factory = _row_factory
        rows = conn.execute(
            """
            SELECT reseller_name, phone, address FROM orders
            WHERE reseller_name LIKE ? AND reseller_name != ''
            ORDER BY id DESC
            LIMIT ?
            """,
            (f"%{clean_q}%", limit),
        ).fetchall()
        return [dict(row) for row in rows]


def get_order_profile_by_name(reseller_name: str) -> dict | None:
    """Busca telefone/endereço de revenda em pedidos anteriores."""
    clean_q = reseller_name.strip()
    if not clean_q:
        return None
    with get_connection() as conn:
        conn.row_factory = _row_factory
        row = conn.execute(
            """
            SELECT phone, address FROM orders
            WHERE reseller_name LIKE ? ORDER BY id DESC LIMIT 1
            """,
            (clean_q,),
        ).fetchone()
        return dict(row) if row else None


def _row_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
