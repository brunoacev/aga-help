"""Parser de arquivos VCF (vCard)."""

from __future__ import annotations

import re

from utils.sanitization import MAX_VCF_CONTACTS, sanitize_name, sanitize_phone


def parse_vcf_content(vcf_text: str) -> list[tuple[str, str]]:
    """Extrai contatos (nome, telefone) de conteúdo VCF."""
    contacts: list[tuple[str, str]] = []
    seen_phones: set[str] = set()
    cards = re.split(r"END:VCARD", vcf_text, flags=re.IGNORECASE)

    for card in cards:
        if not card.strip() or len(contacts) >= MAX_VCF_CONTACTS:
            break

        name = _extract_name(card)
        phone = _extract_phone(card)

        if name and phone:
            clean_name = sanitize_name(name)
            clean_phone = sanitize_phone(phone)
            digits_key = "".join(filter(str.isdigit, clean_phone))
            if digits_key and digits_key not in seen_phones:
                seen_phones.add(digits_key)
                contacts.append((clean_name, clean_phone))

    return contacts


def _extract_name(card: str) -> str:
    fn_match = re.search(r"^FN(?:;[^:]*)?:(.*)$", card, re.MULTILINE | re.IGNORECASE)
    if fn_match:
        return fn_match.group(1).strip()

    n_match = re.search(r"^N(?:;[^:]*)?:(.*)$", card, re.MULTILINE | re.IGNORECASE)
    if not n_match:
        return ""

    parts = n_match.group(1).split(";")
    family = parts[0].strip() if len(parts) > 0 else ""
    given = parts[1].strip() if len(parts) > 1 else ""
    middle = parts[2].strip() if len(parts) > 2 else ""
    name_parts = [p for p in (given, middle, family) if p]
    return " ".join(name_parts)


def _extract_phone(card: str) -> str:
    tel_matches = re.findall(r"^TEL(?:;[^:]*)?:(.*)$", card, re.MULTILINE | re.IGNORECASE)
    for raw_tel in tel_matches:
        digits = "".join(filter(str.isdigit, raw_tel))
        if digits.startswith("55") and len(digits) in (12, 13):
            digits = digits[2:]

        if len(digits) in (10, 11):
            if len(digits) == 11:
                return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        if len(digits) >= 8:
            return raw_tel.strip()
    return ""
