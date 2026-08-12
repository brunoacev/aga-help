"""Testes do parser VCF."""

from core.services.vcf_parser import parse_vcf_content


SAMPLE_VCF = """BEGIN:VCARD
VERSION:3.0
FN:João Silva
TEL;TYPE=CELL:(85) 99876-5432
END:VCARD
BEGIN:VCARD
VERSION:3.0
N:;Maria;Santos;;
TEL:85988776655
END:VCARD
"""


def test_parse_vcf_extracts_contacts():
    contacts = parse_vcf_content(SAMPLE_VCF)
    assert len(contacts) == 2
    names = {c[0] for c in contacts}
    assert "João Silva" in names
    assert "Maria Santos" in names


def test_parse_vcf_deduplicates_phones():
    duplicate_vcf = SAMPLE_VCF + """BEGIN:VCARD
FN:João Duplicado
TEL:(85) 99876-5432
END:VCARD
"""
    contacts = parse_vcf_content(duplicate_vcf)
    assert len(contacts) == 2


def test_parse_vcf_empty_input():
    assert parse_vcf_content("") == []
