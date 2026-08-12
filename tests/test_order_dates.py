"""Testes de datas de pedidos."""

from datetime import datetime

from utils.order_dates import (
    format_order_date_label,
    resolve_order_billing_date,
    resolve_order_created_date,
)


def test_format_order_date_label_from_entry_date():
    order = {"entry_date": "11/08/2026", "created_at": ""}
    assert format_order_date_label(order) == "📅 11/08/2026"


def test_resolve_billing_date_fallback():
    fallback = datetime(2026, 8, 11, 10, 0, 0)
    order = {"status": "Faturado", "value": 100.0}
    assert resolve_order_billing_date(order, fallback=fallback) == fallback


def test_resolve_created_date_from_timestamp():
    order = {"created_at": "2026-08-11 14:30:00"}
    dt = resolve_order_created_date(order)
    assert dt.day == 11 and dt.month == 8
