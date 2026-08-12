"""Testes de geração de QR Code."""

import base64

from utils.qr_code import generate_qr_base64


def test_generate_qr_base64_returns_png_payload():
    result = generate_qr_base64("aga-help-test-session")
    assert isinstance(result, str)
    assert len(result) > 100
    decoded = base64.b64decode(result)
    assert decoded.startswith(b"\x89PNG")


def test_generate_qr_base64_uses_fallback_for_empty_string():
    first = generate_qr_base64("")
    second = generate_qr_base64("   ")
    assert first
    assert second
