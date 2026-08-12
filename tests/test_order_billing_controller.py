"""Testes do controller de conclusão de faturamento."""

from controllers.order_billing_controller import (
    can_modify_billed_order,
    is_order_billed,
    is_order_billing_locked,
    sort_faturado_orders,
)


def test_is_order_billed_reads_sqlite_flag():
    assert not is_order_billed({"is_billed": 0})
    assert is_order_billed({"is_billed": 1})


def test_billing_lock_blocks_common_user():
    order = {"is_billed": 1, "status": "Faturado"}
    assert is_order_billing_locked(order, is_master=False)
    assert not is_order_billing_locked(order, is_master=True)


def test_master_can_modify_billed_orders():
    assert not can_modify_billed_order(is_master=False)
    assert can_modify_billed_order(is_master=True)


def test_sort_faturado_orders_pending_first():
    orders = [
        {"id": 1, "is_billed": 1},
        {"id": 2, "is_billed": 0},
        {"id": 3, "is_billed": 1},
        {"id": 4, "is_billed": 0},
    ]
    pending, completed = sort_faturado_orders(orders)
    assert [item["id"] for item in pending] == [2, 4]
    assert [item["id"] for item in completed] == [1, 3]
