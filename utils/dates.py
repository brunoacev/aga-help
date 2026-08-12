"""Utilitários de data."""

from __future__ import annotations

from datetime import datetime, timedelta


def add_business_days(from_date: datetime, num_days: int) -> datetime:
    """Soma dias úteis (segunda a sexta) a partir de uma data."""
    current = from_date
    added = 0
    while added < num_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current
