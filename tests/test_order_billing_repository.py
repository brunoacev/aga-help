"""Testes de conclusão de faturamento no repositório."""

from core.kanban_stages import STAGE_FATURADO, STAGE_PRONTO
from core.db.orders_repository import add_order, get_orders, mark_order_billed, update_order_status
from core.services.order_service import complete_order_billing


def test_mark_order_billed_persists_flag():
    add_order(
        order_number="900",
        reseller_name="Revenda Billing",
        phone="",
        address="",
        value=100.0,
        entry_date="11/08/2026",
        deadline_date="12/08/2026",
        description="Pedido billing",
        status=STAGE_FATURADO,
    )
    order_id = get_orders()[0]["id"]
    mark_order_billed(order_id, is_billed=True)
    saved = get_orders()[0]
    assert saved["is_billed"] == 1


def test_complete_order_billing_service():
    add_order(
        order_number="901",
        reseller_name="Revenda Billing 2",
        phone="",
        address="",
        value=200.0,
        entry_date="11/08/2026",
        deadline_date="12/08/2026",
        description="Pedido billing 2",
        status=STAGE_FATURADO,
    )
    order_id = get_orders()[0]["id"]
    complete_order_billing(order_id)
    assert get_orders()[0]["is_billed"] == 1


def test_leaving_faturado_resets_is_billed():
    add_order(
        order_number="902",
        reseller_name="Revenda Billing 3",
        phone="",
        address="",
        value=300.0,
        entry_date="11/08/2026",
        deadline_date="12/08/2026",
        description="Pedido billing 3",
        status=STAGE_FATURADO,
    )
    order_id = get_orders()[0]["id"]
    mark_order_billed(order_id, is_billed=True)
    update_order_status(order_id, STAGE_PRONTO)
    saved = get_orders()[0]
    assert saved["status"] == STAGE_PRONTO
    assert saved["is_billed"] == 0
