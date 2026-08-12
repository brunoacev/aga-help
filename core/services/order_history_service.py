"""Serviço de auditoria por pedido."""

from __future__ import annotations

from core.db.order_history_repository import add_order_history, get_order_history


def record_order_action(order_id: int, user_handle: str, action_description: str) -> None:
    if not order_id:
        return
    add_order_history(order_id, user_handle, action_description)


def list_order_actions(order_id: int) -> list[dict]:
    return get_order_history(order_id)
