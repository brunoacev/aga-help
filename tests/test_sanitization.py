"""Testes de sanitização."""

from utils.sanitization import sanitize_name, sanitize_phone, validate_vcf_input


def test_sanitize_name_strips_control_chars():
    assert sanitize_name('João\r\n"Teste') == "JoãoTeste"


def test_sanitize_phone_brazilian_format():
    assert sanitize_phone("85999887766") == "(85) 99988-7766"


def test_validate_vcf_input_rejects_empty():
    valid, msg = validate_vcf_input("")
    assert not valid
    assert "Cole" in msg


def test_validate_vcf_input_rejects_oversized():
    valid, msg = validate_vcf_input("x" * 600_000)
    assert not valid
    assert "limite" in msg.lower()
