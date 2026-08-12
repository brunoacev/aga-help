"""Testes de normalização para busca textual."""

from core.services.catalog_service import filter_components
from utils.text_search import matches_search_query, normalize_search_text


def test_normalize_search_text_removes_accents():
    assert normalize_search_text("Lâmina") == "lamina"
    assert normalize_search_text("Rolô") == "rolo"
    assert normalize_search_text("Serviço") == "servico"
    assert normalize_search_text("LÂMINA") == "lamina"


def test_matches_search_query_ignores_accents():
    assert matches_search_query("lam", "Presilha da Lâmina de Madeira")
    assert matches_search_query("rolo", "Capa Rolô Suporte Curto")
    assert matches_search_query("servico", "Serviço em Cortina")
    assert not matches_search_query("xyz", "Comando Pequeno")


def test_filter_components_accent_insensitive():
    results = filter_components("lam", limit=20)
    assert results
    assert all("lâmina" in item["name"].lower() or "lamina" in normalize_search_text(item["name"]) for item in results)


def test_filter_components_finds_rolo_category():
    results = filter_components("rolo", limit=5)
    assert results
    assert any(
        "rolo" in normalize_search_text(item["name"])
        or normalize_search_text(item["category"]) == "rolo"
        for item in results
    )
