"""Testes do resumo exibido no card do Kanban."""

from utils.order_card_display import build_card_summary_lines, get_card_notes, get_service_label


def test_card_hides_component_list_in_notes():
    order = {
        "description": "2x 5060 - Comando Pequeno (Branco), 1x 4085 - Tubo Alumínio 38mm (2,5m)",
        "items_json": '[{"code":"5060","name":"Comando","qty":2,"dim":""}]',
        "service_type": "componentes",
    }
    assert get_card_notes(order) == ""


def test_card_shows_curtain_description_as_notes():
    order = {
        "description": "Cortina rolô blackout sala 02",
        "service_type": "rolo",
        "width": "2,5",
        "height": "2,8",
    }
    assert "blackout" in get_card_notes(order)
    assert get_service_label(order) == "Serviço em Cortina Rolô"


def test_build_card_summary_lines():
    order = {
        "description": "2x 5060 - Comando",
        "items_json": '[{"code":"5060","name":"Comando","qty":2,"dim":""}]',
        "service_type": "componentes",
        "width": "1,2",
        "height": "2,0",
    }
    lines = build_card_summary_lines(order)
    assert any("Venda de Peças" in line for line in lines)
    assert any("Medidas:" in line for line in lines)
    assert not any("5060" in line for line in lines)
