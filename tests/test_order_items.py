"""Testes de extração de itens de pedidos."""

from utils.order_items import (
    extract_order_items,
    format_item_qty,
    normalize_order_item,
    parse_items_from_description,
    serialize_order_items,
)


def test_parse_items_from_description():
    description = "2x 5060 - Comando Pequeno (Branco), 1x 4085 - Tubo Alumínio 38mm (2,5m)"
    items = parse_items_from_description(description)
    assert len(items) == 2
    assert items[0]["code"] == "5060"
    assert items[0]["qty"] == 2
    assert items[0]["qty_display"] == "2 un"
    assert items[1]["dim"] == "2,5"
    assert items[1]["qty_display"] == "2,5m"


def test_extract_order_items_prefers_json():
    order = {
        "description": "legado",
        "items_json": '[{"code":"1248","name":"Cavelete","qty":1,"dim":""}]',
    }
    items = extract_order_items(order)
    assert len(items) == 1
    assert items[0]["code"] == "1248"


def test_extract_order_items_empty():
    assert extract_order_items({"description": "Serviço de cortina rolô"}) == []


def test_format_item_qty_and_serialize():
    item = normalize_order_item({"code": "4085", "name": "Tubo", "qty": 1, "dim": "3,2"})
    assert format_item_qty(item) == "3,2m"
    payload = serialize_order_items([item])
    assert '"4085"' in payload
