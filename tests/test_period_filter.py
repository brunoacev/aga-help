"""Testes de filtro temporal."""

from datetime import datetime

from utils.period_filter import get_period_bounds, shift_reference_date


def test_monthly_period_bounds():
    ref = datetime(2026, 8, 15)
    start, end = get_period_bounds("Mensal", ref)
    assert start.day == 1 and start.month == 8
    assert end.day == 31 and end.month == 8


def test_shift_monthly_reference():
    ref = datetime(2026, 8, 15)
    next_ref = shift_reference_date("Mensal", ref, 1)
    assert next_ref.month == 9 and next_ref.day == 1
