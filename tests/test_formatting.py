"""Testes de formatação e parsing."""

from utils.formatting import format_meters, parse_meters


def test_parse_meters_accepts_brazilian_decimal():
    assert parse_meters("2,30") == 2.3


def test_parse_meters_rejects_empty_and_zero():
    assert parse_meters("") is None
    assert parse_meters("0") is None


def test_format_meters():
    assert format_meters(2.3) == "2,3"
    assert format_meters(2.0) == "2"
