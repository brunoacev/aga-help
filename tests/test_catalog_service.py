"""Testes do serviço de catálogo."""

from core.services.catalog_service import categorize_materials, filter_components, is_meter_item


def test_is_meter_item_by_keyword():
    assert is_meter_item({"name": "Trilho 50mm Super Mono", "code": "10015"})
    assert not is_meter_item({"name": "Freio", "code": "1257"})


def test_is_meter_item_by_unit_type():
    assert is_meter_item({"name": "Item", "unit_type": "meter"})
    assert not is_meter_item({"name": "Item", "unit_type": "unit"})


def test_filter_components_by_code():
    results = filter_components("1248", limit=5)
    assert len(results) >= 1
    assert any(r["code"] == "1248" for r in results)


def test_categorize_materials():
    items = [
        {"code": "1", "name": "Lâmina", "category": "Horizontais"},
        {"code": "2", "name": "Tecido", "category": "Verticais e Tecidos"},
        {"code": "3", "name": "Trilho", "category": "Perfil"},
        {"code": "4", "name": "Comando", "category": "TOP"},
    ]
    buckets = categorize_materials(items)
    assert len(buckets["horizontals"]) == 1
    assert len(buckets["verticals"]) == 1
    assert len(buckets["profiles"]) == 1
    assert len(buckets["top"]) == 1
