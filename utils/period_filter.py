"""Utilitários de filtro temporal para relatórios."""

from __future__ import annotations

from datetime import datetime, timedelta

PERIOD_LABELS = (
    "Diário",
    "Semanal",
    "Quinzenal",
    "Mensal",
    "Semestral",
    "Anual",
)


def _month_shift(year: int, month: int, delta: int) -> tuple[int, int]:
    month += delta
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return year, month


def get_period_bounds(period: str, reference: datetime) -> tuple[datetime, datetime]:
    """Retorna intervalo [início, fim] inclusivo para o período e data de referência."""
    ref = reference.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "Diário":
        start = ref
        end = ref.replace(hour=23, minute=59, second=59)

    elif period == "Semanal":
        start = ref - timedelta(days=ref.weekday())
        end = (start + timedelta(days=6)).replace(hour=23, minute=59, second=59)

    elif period == "Quinzenal":
        if ref.day <= 15:
            start = ref.replace(day=1)
            end = ref.replace(day=15, hour=23, minute=59, second=59)
        else:
            last_day = (ref.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            start = ref.replace(day=16)
            end = last_day.replace(hour=23, minute=59, second=59)

    elif period == "Mensal":
        start = ref.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = (next_month - timedelta(days=1)).replace(hour=23, minute=59, second=59)

    elif period == "Semestral":
        if ref.month <= 6:
            start = ref.replace(month=1, day=1)
            end = ref.replace(month=6, day=30, hour=23, minute=59, second=59)
        else:
            start = ref.replace(month=7, day=1)
            end = ref.replace(month=12, day=31, hour=23, minute=59, second=59)

    elif period == "Anual":
        start = ref.replace(month=1, day=1)
        end = ref.replace(month=12, day=31, hour=23, minute=59, second=59)

    else:
        start = ref.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = (next_month - timedelta(days=1)).replace(hour=23, minute=59, second=59)

    return start, end


def shift_reference_date(period: str, reference: datetime, direction: int) -> datetime:
    """Avança ou retrocede a data de referência conforme o tipo de período."""
    step = 1 if direction >= 0 else -1
    ref = reference.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "Diário":
        return ref + timedelta(days=step)

    if period == "Semanal":
        return ref + timedelta(days=7 * step)

    if period == "Quinzenal":
        if step > 0:
            if ref.day <= 15:
                last_day = (ref.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                return last_day.replace(hour=0, minute=0, second=0, microsecond=0)
            return (ref.replace(day=1) + timedelta(days=32)).replace(day=1)
        if ref.day <= 15:
            prev_month_last = ref.replace(day=1) - timedelta(days=1)
            return prev_month_last.replace(day=16, hour=0, minute=0, second=0, microsecond=0)
        return ref.replace(day=1)

    if period == "Mensal":
        year, month = _month_shift(ref.year, ref.month, step)
        return ref.replace(year=year, month=month, day=1)

    if period == "Semestral":
        if ref.month <= 6:
            if step > 0:
                return ref.replace(month=7, day=1)
            return ref.replace(year=ref.year - 1, month=7, day=1)
        if step > 0:
            return ref.replace(year=ref.year + 1, month=1, day=1)
        return ref.replace(month=1, day=1)

    if period == "Anual":
        return ref.replace(year=ref.year + step, month=1, day=1)

    year, month = _month_shift(ref.year, ref.month, step)
    return ref.replace(year=year, month=month, day=1)


def format_period_label(period: str, start: datetime, end: datetime) -> str:
    """Texto legível do intervalo selecionado."""
    if period == "Diário":
        return start.strftime("%d/%m/%Y")
    if period == "Anual":
        return str(start.year)
    if period == "Mensal":
        return start.strftime("%m/%Y")
    return f"{start.strftime('%d/%m/%Y')} — {end.strftime('%d/%m/%Y')}"
