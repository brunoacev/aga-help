"""Testes de leitura de arquivos VCF."""

from __future__ import annotations

from pathlib import Path

import flet as ft

from utils.vcf_io import decode_vcf_bytes, read_vcf_from_picker_file, read_vcf_text_from_path


def test_decode_vcf_bytes_utf8():
    data = b"BEGIN:VCARD\nFN:Test\nEND:VCARD"
    text, error = decode_vcf_bytes(data)
    assert error == ""
    assert "BEGIN:VCARD" in text


def test_decode_vcf_bytes_empty():
    text, error = decode_vcf_bytes(b"")
    assert text == ""
    assert "vazio" in error.lower()


def test_read_vcf_text_from_path(tmp_path: Path):
    vcf_path = tmp_path / "contatos.vcf"
    vcf_path.write_text("BEGIN:VCARD\nFN:Revenda\nEND:VCARD", encoding="utf-8")

    text, error = read_vcf_text_from_path(vcf_path)
    assert error == ""
    assert "Revenda" in text


def test_read_vcf_text_from_path_rejects_wrong_extension(tmp_path: Path):
    txt_path = tmp_path / "notas.txt"
    txt_path.write_text("hello", encoding="utf-8")

    _, error = read_vcf_text_from_path(txt_path)
    assert ".VCF" in error


def test_read_vcf_from_picker_file_uses_bytes():
    file = ft.FilePickerFile(
        id=1,
        name="agenda.vcf",
        size=20,
        bytes=b"BEGIN:VCARD\nFN:A\nEND:VCARD",
    )
    text, error = read_vcf_from_picker_file(file)
    assert error == ""
    assert "FN:A" in text
