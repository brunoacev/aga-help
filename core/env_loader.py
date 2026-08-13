"""Carrega variáveis do arquivo `.env` na raiz do projeto."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ENV_PATH = _PROJECT_ROOT / ".env"


def load_project_env() -> None:
    """Lê `.env` da raiz com override para priorizar credenciais locais."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    if _ENV_PATH.is_file():
        # utf-8-sig remove BOM do PowerShell/Windows que quebra SUPABASE_URL
        content = _ENV_PATH.read_text(encoding="utf-8-sig")
        load_dotenv(stream=StringIO(content), override=True)
    else:
        load_dotenv(override=True)


def project_env_path() -> Path:
    return _ENV_PATH
