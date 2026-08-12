"""Utilitários de parsing e formatação de datas de pedidos."""

from __future__ import annotations

from datetime import datetime

ORDER_TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S"
ORDER_TIMESTAMP_FMT_LEGACY = "%Y-%m-%d %H:%M"
ENTRY_DATE_FMT = "%d/%m/%Y"

_DATETIME_FORMATS = (ORDER_TIMESTAMP_FMT, ORDER_TIMESTAMP_FMT_LEGACY, ENTRY_DATE_FMT)


def _parse_datetime(raw: str | None) -> datetime | None:
    if not raw or not str(raw).strip():
        return None
    text = str(raw).strip()
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def current_order_timestamp() -> str:
    """Timestamp ISO local para persistência em novos pedidos."""
    return datetime.now().strftime(ORDER_TIMESTAMP_FMT)


def normalize_order_created_at(order: dict) -> dict:
    """Preenche created_at ausente em memória (fallback para pedidos legados)."""
    if (order.get("created_at") or "").strip():
        return order
    fallback = current_order_timestamp()
    return {**order, "created_at": fallback}


def parse_order_created_date(order: dict) -> datetime | None:
    """Data de criação/orçamento do pedido."""
    for field in ("created_at", "entry_date", "order_date"):
        parsed = _parse_datetime(order.get(field))
        if parsed:
            return parsed
    return None


def parse_order_billing_date(order: dict) -> datetime | None:
    """Data de faturamento/conclusão comercial do pedido."""
    for field in ("billed_at", "created_at", "entry_date"):
        parsed = _parse_datetime(order.get(field))
        if parsed:
            return parsed
    return None


def resolve_order_created_date(order: dict, *, fallback: datetime | None = None) -> datetime:
    """Garante data de criação para exibição e relatórios."""
    return parse_order_created_date(order) or fallback or datetime.now()


def resolve_order_billing_date(order: dict, *, fallback: datetime | None = None) -> datetime:
    """Garante data de faturamento — usa fallback para pedidos legados sem timestamp."""
    return parse_order_billing_date(order) or fallback or datetime.now()


def format_order_date_label(order: dict) -> str:
    """Rótulo compacto de data para cards do Kanban."""
    created = resolve_order_created_date(order)
    return f"📅 {created.strftime(ENTRY_DATE_FMT)}"


def format_order_datetime(order: dict, *, billing: bool = False) -> str:
    """Formata data do pedido para tabelas."""
    dt = resolve_order_billing_date(order) if billing else resolve_order_created_date(order)
    return dt.strftime(ENTRY_DATE_FMT)
