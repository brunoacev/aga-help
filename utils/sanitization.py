"""Sanitização de entradas do usuário."""

from __future__ import annotations

import re

MAX_TEXT_LENGTH = 500
MAX_NAME_LENGTH = 120
MAX_VCF_SIZE = 500_000
MAX_VCF_CONTACTS = 5000

PHONE_PATTERN = re.compile(r"^[\d\s\(\)\+\-\.]{8,20}$")


def sanitize_text(value: str, *, max_length: int = MAX_TEXT_LENGTH) -> str:
    """Remove caracteres de controle e limita tamanho."""
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\r\n\"\\]", "", (value or "").strip())
    return clean[:max_length]


def sanitize_name(value: str) -> str:
    """Sanitiza nome de contato ou revenda."""
    return sanitize_text(value, max_length=MAX_NAME_LENGTH)


def sanitize_phone(value: str) -> str:
    """Sanitiza telefone; retorna vazio se formato inválido."""
    clean = sanitize_text(value, max_length=30)
    if not clean:
        return ""
    digits = "".join(filter(str.isdigit, clean))
    if len(digits) in (10, 11):
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    if PHONE_PATTERN.match(clean):
        return clean
    return clean if len(digits) >= 8 else ""


def validate_vcf_input(vcf_text: str) -> tuple[bool, str]:
    """Valida tamanho do conteúdo VCF antes do processamento."""
    if not (vcf_text or "").strip():
        return False, "Cole o texto VCF antes de importar."
    if len(vcf_text) > MAX_VCF_SIZE:
        return False, f"Arquivo VCF excede o limite de {MAX_VCF_SIZE // 1000} KB."
    return True, ""
