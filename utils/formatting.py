"""Formatação de valores e textos."""

from __future__ import annotations


def safe_float(val) -> float:
    """Converte valor monetário/numerico com fallback seguro."""
    try:
        return float(val) if val is not None else 0.0
    except (ValueError, TypeError):
        return 0.0


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


def parse_meters(value_raw: str) -> float | None:
    """Converte metragem textual (ex: 2,30 ou 2.30) em float positivo."""
    clean = (value_raw or "").strip().replace("m", "").replace("M", "").strip()
    if not clean:
        return None
    if "," in clean:
        clean = clean.replace(".", "").replace(",", ".")
    try:
        value = float(clean)
    except ValueError:
        return None
    return value if value > 0 else None


def format_meters(value: float) -> str:
    """Formata metragem para exibição no padrão brasileiro."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")
