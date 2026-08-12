"""Utilitários de busca textual."""

from __future__ import annotations

import unicodedata


def normalize_search_text(text: str) -> str:
    """Remove acentos e converte para minúsculas para comparação de busca."""
    normalized = unicodedata.normalize("NFD", text or "")
    without_accents = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return without_accents.lower()


def matches_search_query(query: str, *values: str) -> bool:
    """Verifica se a consulta aparece em algum dos valores (ignorando acentos)."""
    needle = normalize_search_text(query)
    if not needle:
        return True
    return any(needle in normalize_search_text(value) for value in values)
