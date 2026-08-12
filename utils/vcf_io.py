"""Leitura e decodificação de arquivos VCF para importação."""

from __future__ import annotations

from pathlib import Path

import flet as ft

_VCF_ENCODINGS = ("utf-8", "utf-8-sig", "latin-1", "cp1252")


def decode_vcf_bytes(data: bytes) -> tuple[str, str]:
    """
    Decodifica bytes de um arquivo VCF.
    Retorna (texto, mensagem_erro ou vazio).
    """
    if not data:
        return "", "O arquivo VCF está vazio."

    for encoding in _VCF_ENCODINGS:
        try:
            return data.decode(encoding), ""
        except UnicodeDecodeError:
            continue

    return "", "Não foi possível decodificar o arquivo VCF."


def read_vcf_text_from_path(path: str | Path) -> tuple[str, str]:
    """Lê conteúdo VCF a partir de um caminho no disco."""
    file_path = Path(path)
    if file_path.suffix.lower() != ".vcf":
        return "", "Selecione um arquivo com extensão .VCF."

    try:
        data = file_path.read_bytes()
    except OSError as exc:
        return "", f"Erro ao ler o arquivo: {exc}"

    return decode_vcf_bytes(data)


def read_vcf_from_picker_file(file: ft.FilePickerFile) -> tuple[str, str]:
    """
    Obtém texto VCF de um arquivo selecionado via FilePicker.
    Usa bytes quando disponíveis; caso contrário, lê pelo path (desktop).
    """
    name = (file.name or "").lower()
    if name and not name.endswith(".vcf"):
        return "", "Selecione um arquivo com extensão .VCF."

    if file.bytes:
        text, error = decode_vcf_bytes(file.bytes)
        if not error:
            return text, ""
        if file.path:
            return read_vcf_text_from_path(file.path)
        return text, error

    if file.path:
        return read_vcf_text_from_path(file.path)

    return "", "Não foi possível ler o conteúdo do arquivo VCF."
