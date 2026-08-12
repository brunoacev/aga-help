"""Utilitários de parsing de datas de pedidos."""

from __future__ import annotations

from datetime import datetime


def parse_order_billing_date(order: dict) -> datetime | None:
    """Obtém a data de faturamento/conclusão usada nos relatórios."""
    for raw, fmt in (
        (order.get("billed_at"), "%Y-%m-%d %H:%M"),
        (order.get("created_at"), "%Y-%m-%d %H:%M"),
    ):
        if raw:
            try:
                return datetime.strptime(str(raw).strip(), fmt)
            except ValueError:
                continue

    entry = (order.get("entry_date") or "").strip()
    if entry:
        try:
            return datetime.strptime(entry, "%d/%m/%Y")
        except ValueError:
            pass
    return None
