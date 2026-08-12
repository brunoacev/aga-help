"""Testes do serviço de pedidos."""

from core.services.order_service import create_order, get_orders, validate_order_form


def test_validate_order_form_missing_fields():
    valid, missing = validate_order_form({})
    assert not valid
    assert "Revenda" in missing
    assert "Nº do Pedido" in missing


def test_create_order_success():
    success, error = create_order(
        {
            "reseller_name": "Revenda Teste",
            "order_number": "12345",
            "deadline_days": "3",
            "service_type": "componentes",
            "description": "Pedido de teste",
            "phone": "(85) 99999-9999",
            "address": "Rua Teste",
            "value": "150,00",
        }
    )
    assert success
    assert error == ""
    orders = get_orders()
    assert len(orders) == 1
    assert orders[0]["reseller_name"] == "Revenda Teste"
    assert orders[0]["value"] == 150.0


def test_create_order_rejects_empty_required():
    success, error = create_order({"reseller_name": "", "order_number": ""})
    assert not success
    assert "obrigatórios" in error.lower()
