"""Regras de conclusão de faturamento e travas de edição."""

from __future__ import annotations

BILLED_STAGE = "Faturado"


def is_order_billed(order: dict) -> bool:
    """Indica se o pedido foi confirmado/concluído na coluna Faturado."""
    value = order.get("is_billed", 0)
    return bool(value)


def can_modify_billed_order(*, is_master: bool = False) -> bool:
    """Future-proof: apenas perfil master/admin poderá editar pedidos concluídos."""
    return is_master


def is_order_billing_locked(order: dict, *, is_master: bool = False) -> bool:
    """Pedidos concluídos ficam bloqueados para usuários comuns."""
    if not is_order_billed(order):
        return False
    return not can_modify_billed_order(is_master=is_master)


def can_move_order(order: dict, *, is_master: bool = False) -> bool:
    return not is_order_billing_locked(order, is_master=is_master)


def can_delete_order(order: dict, *, is_master: bool = False) -> bool:
    return not is_order_billing_locked(order, is_master=is_master)


def can_view_order_details(order: dict, *, is_master: bool = False) -> bool:
    return not is_order_billing_locked(order, is_master=is_master)


def sort_faturado_orders(orders: list[dict]) -> tuple[list[dict], list[dict]]:
    """Separa pendentes (topo) e concluídos (rodapé) na coluna Faturado."""
    pending = [order for order in orders if not is_order_billed(order)]
    completed = [order for order in orders if is_order_billed(order)]
    return pending, completed
