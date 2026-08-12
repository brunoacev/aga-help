"""Testes de validação condicional do formulário de pedido."""

from controllers.order_form_controller import OrderFormController


def _base_form(**overrides):
    data = {
        "reseller_name": "Revenda Teste",
        "order_number": "12345",
        "deadline_days": "3",
        "service_type": "componentes",
        "description": "",
        "phone": "",
        "address": "",
        "value": "0",
    }
    data.update(overrides)
    return data


def test_validate_requires_box1_and_box2():
    controller = OrderFormController()
    valid, error, fields = controller.validate(_base_form(reseller_name="", order_number=""))
    assert not valid
    assert "obrigatórios" in error.lower()
    assert "reseller_name" in fields
    assert "order_number" in fields


def test_validate_parts_requires_components():
    controller = OrderFormController()
    valid, error, fields = controller.validate(_base_form(service_type="componentes"))
    assert not valid
    assert "componente" in error.lower()
    assert fields == {"components"}


def test_validate_parts_allows_empty_description():
    controller = OrderFormController()
    controller.add_component({"code": "5060", "name": "Comando"}, "", "1")
    valid, error, fields = controller.validate(_base_form(service_type="componentes", description=""))
    assert valid
    assert error == ""
    assert fields == set()


def test_validate_curtain_requires_description():
    controller = OrderFormController()
    valid, error, fields = controller.validate(_base_form(service_type="rolo", description=""))
    assert not valid
    assert "box 4" in error.lower() or "descrição" in error.lower()
    assert fields == {"description"}


def test_validate_curtain_allows_empty_components():
    controller = OrderFormController()
    valid, error, fields = controller.validate(
        _base_form(service_type="horizontal", description="Cortina 2,50m x 2,80m")
    )
    assert valid
    assert error == ""
    assert fields == set()
