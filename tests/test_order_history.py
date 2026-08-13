"""Testes de auditoria por pedido."""

from core.kanban_stages import STAGE_FATURADO, STAGE_PRONTO, STAGE_PRODUCAO
from core.services.order_history_service import list_order_actions, record_order_action
from core.services.order_service import create_order, get_orders, update_order_status


def _sample_form():
    return {
        "reseller_name": "Revenda Audit",
        "order_number": "AUD-001",
        "deadline_days": "3",
        "service_type": "componentes",
        "description": "Pedido para auditoria",
        "value": "100,00",
    }


def test_create_order_records_history_and_created_by():
    success, error = create_order(_sample_form(), created_by="@suporte")
    assert success, error
    orders = get_orders()
    assert orders[0]["created_by"] == "@suporte"
    assert orders[0]["status"] == STAGE_PRODUCAO
    history = list_order_actions(orders[0]["id"])
    assert len(history) >= 1
    assert "@suporte" in history[0]["action_description"]
    assert "criou" in history[0]["action_description"].lower()


def test_move_order_records_history():
    create_order(_sample_form(), created_by="@rota")
    order_id = get_orders()[0]["id"]
    update_order_status(order_id, STAGE_PRONTO, user_handle="@rota", old_status=STAGE_PRODUCAO)
    history = list_order_actions(order_id)
    descriptions = " ".join(item["action_description"] for item in history)
    assert "moveu" in descriptions.lower()
    assert STAGE_PRONTO in descriptions


def test_record_order_action_direct():
    create_order(_sample_form(), created_by="@suporte")
    order_id = get_orders()[0]["id"]
    record_order_action(order_id, "@suporte", "@suporte testou ação manual")
    history = list_order_actions(order_id)
    assert any("ação manual" in item["action_description"] for item in history)
