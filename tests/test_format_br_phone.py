"""Testes de formatação de telefone BR."""

from utils.formatting import format_br_phone


def test_format_br_phone_mobile_with_country_code():
    assert format_br_phone("5585999999999") == "+55 (85) 99999-9999"


def test_format_br_phone_mobile_without_country_code():
    assert format_br_phone("85999999999") == "+55 (85) 99999-9999"


def test_format_br_phone_landline():
    assert format_br_phone("558533221234") == "+55 (85) 3322-1234"


def test_format_br_phone_jid():
    assert format_br_phone("5585999999999@s.whatsapp.net") == "+55 (85) 99999-9999"
