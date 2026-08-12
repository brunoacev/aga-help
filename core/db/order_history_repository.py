"""Histórico de auditoria por pedido (SQLite local + Supabase)."""

from __future__ import annotations

from datetime import datetime

from core.db.connection import get_connection
from core.supabase_client import get_supabase

HISTORY_TIMESTAMP_FMT = "%d/%m/%Y %H:%M"


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _display_timestamp(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(raw, fmt).strftime(HISTORY_TIMESTAMP_FMT)
        except ValueError:
            continue
    return raw


def insert_history_local(order_id: int, user_handle: str, action_description: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO order_history (order_id, user_handle, action_description, created_at, synced)
            VALUES (?, ?, ?, ?, 0)
            """,
            (int(order_id), user_handle, action_description, _now_str()),
        )
        conn.commit()


def insert_history_remote(order_id: int, user_handle: str, action_description: str) -> bool:
    supabase = get_supabase()
    client = supabase.get_client()
    if not client or not supabase.is_online:
        return False
    try:
        client.table("order_history").insert(
            {
                "order_id": int(order_id),
                "user_handle": user_handle,
                "action_description": action_description,
                "created_at": _now_str(),
            }
        ).execute()
        return True
    except Exception:
        return False


def add_order_history(order_id: int, user_handle: str, action_description: str) -> None:
    handle = (user_handle or "@sistema").strip()
    description = (action_description or "").strip()
    if not description:
        return
    insert_history_local(order_id, handle, description)
    if insert_history_remote(order_id, handle, description):
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE order_history
                SET synced = 1
                WHERE id = (
                    SELECT id FROM order_history
                    WHERE order_id = ? AND user_handle = ? AND action_description = ?
                    ORDER BY id DESC LIMIT 1
                )
                """,
                (int(order_id), handle, description),
            )
            conn.commit()


def get_order_history(order_id: int) -> list[dict]:
    entries: list[dict] = []
    supabase = get_supabase()
    client = supabase.get_client()
    if client and supabase.is_online:
        try:
            response = (
                client.table("order_history")
                .select("id, order_id, user_handle, action_description, created_at")
                .eq("order_id", int(order_id))
                .order("created_at")
                .execute()
            )
            for row in response.data or []:
                entries.append(
                    {
                        "id": row.get("id"),
                        "order_id": row.get("order_id"),
                        "user_handle": row.get("user_handle"),
                        "action_description": row.get("action_description"),
                        "created_at": _display_timestamp(str(row.get("created_at") or "")),
                    }
                )
        except Exception:
            entries = []

    if entries:
        return entries

    with get_connection() as conn:
        conn.row_factory = _row_factory
        rows = conn.execute(
            """
            SELECT id, order_id, user_handle, action_description, created_at
            FROM order_history
            WHERE order_id = ?
            ORDER BY id ASC
            """,
            (int(order_id),),
        ).fetchall()
    return [
        {
            **dict(row),
            "created_at": _display_timestamp(str(row.get("created_at") or "")),
        }
        for row in rows
    ]


def _row_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
