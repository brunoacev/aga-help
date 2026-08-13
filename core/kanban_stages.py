"""Etapas oficiais do fluxo Kanban (3 colunas)."""

from __future__ import annotations

from core import colors

STAGE_PRODUCAO = "PRODUCAO"
STAGE_PRONTO = "PRONTO"
STAGE_FATURADO = "FATURADO"

KANBAN_STAGES: tuple[str, str, str] = (STAGE_PRODUCAO, STAGE_PRONTO, STAGE_FATURADO)

STAGE_LABELS: dict[str, str] = {
    STAGE_PRODUCAO: "Produção",
    STAGE_PRONTO: "Pronto",
    STAGE_FATURADO: "Faturado",
}

STAGE_COLORS: dict[str, str] = {
    STAGE_PRODUCAO: colors.COLOR_PRODUCAO,
    STAGE_PRONTO: colors.COLOR_PRONTO,
    STAGE_FATURADO: colors.COLOR_FATURADO,
}

BILLED_STAGE = STAGE_FATURADO

_LEGACY_STATUS_MAP: dict[str, str] = {
    "orçamento": STAGE_PRODUCAO,
    "orcamento": STAGE_PRODUCAO,
    "produção": STAGE_PRODUCAO,
    "producao": STAGE_PRODUCAO,
    STAGE_PRODUCAO.lower(): STAGE_PRODUCAO,
    "pronto": STAGE_PRONTO,
    STAGE_PRONTO.lower(): STAGE_PRONTO,
    "faturado": STAGE_FATURADO,
    STAGE_FATURADO.lower(): STAGE_FATURADO,
}


def stage_label(status: str) -> str:
    normalized = normalize_order_status(status)
    return STAGE_LABELS.get(normalized, normalized)


def normalize_order_status(status: str | None) -> str:
    """Normaliza status legado ou acentuado para PRODUCAO | PRONTO | FATURADO."""
    raw = (status or "").strip()
    if not raw:
        return STAGE_PRODUCAO
    key = raw.lower().replace("ç", "c")
    mapped = _LEGACY_STATUS_MAP.get(key) or _LEGACY_STATUS_MAP.get(raw.lower())
    if mapped:
        return mapped
    upper = raw.upper()
    if upper in KANBAN_STAGES:
        return upper
    return STAGE_PRODUCAO


def is_valid_kanban_status(status: str) -> bool:
    return normalize_order_status(status) in KANBAN_STAGES


def validate_kanban_status(status: str) -> str:
    """Retorna status normalizado ou levanta ValueError."""
    normalized = normalize_order_status(status)
    if normalized not in KANBAN_STAGES:
        raise ValueError(f"Status inválido: {status}")
    return normalized
