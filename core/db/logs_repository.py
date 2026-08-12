"""Repositório de logs de auditoria."""

from __future__ import annotations

from datetime import datetime

from core.db.connection import get_connection
from utils.sanitization import sanitize_text


def add_log(action_type: str, description: str) -> None:
    """Registra ação no log de auditoria."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO logs (action_type, description, created_at)
            VALUES (?, ?, ?)
            """,
            (
                sanitize_text(action_type, max_length=50),
                sanitize_text(description, max_length=500),
                now_str,
            ),
        )
        conn.commit()


def get_logs(limit: int = 50) -> list[dict]:
    """Retorna os logs mais recentes."""
    with get_connection() as conn:
        conn.row_factory = _row_factory
        rows = conn.execute(
            "SELECT * FROM logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def _row_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
