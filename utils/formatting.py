"""Formatação de valores e textos."""

from __future__ import annotations


def format_brl(value: float) -> str:
    """Formata valor monetário no padrão brasileiro."""
    formatted = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


def parse_brl(value_raw: str) -> float:
    """Converte string monetária brasileira em float."""
    clean = (value_raw or "0").strip().replace("R$", "").replace(" ", "")
    if "," in clean:
        clean = clean.replace(".", "").replace(",", ".")
    try:
        return float(clean) if clean else 0.0
    except ValueError:
        return 0.0
