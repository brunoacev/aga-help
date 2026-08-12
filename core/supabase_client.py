"""Cliente Supabase com verificação de conectividade e fallback local."""

from __future__ import annotations

import os
from typing import Any

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    from supabase import Client, create_client
except ImportError:  # pragma: no cover - dependência opcional em runtime mínimo
    Client = Any  # type: ignore[misc, assignment]
    create_client = None  # type: ignore[assignment]


def _resolve_supabase_key() -> str:
    """Lê a chave pública do Supabase com fallbacks comuns de nomenclatura."""
    for env_name in ("SUPABASE_KEY", "SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"):
        value = os.getenv(env_name, "").strip()
        if value:
            return value
    return ""


class SupabaseClient:
    """Singleton leve para acesso ao Supabase via REST."""

    _instance: SupabaseClient | None = None

    def __init__(self) -> None:
        self.url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
        self.key = _resolve_supabase_key()
        self.database_url = os.getenv("DATABASE_URL", "").strip()
        self._client: Client | None = None
        self._online: bool | None = None
        self.last_error = ""

    @classmethod
    def instance(cls) -> SupabaseClient:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.key and create_client is not None)

    def get_client(self) -> Client | None:
        if not self.is_configured:
            return None
        if self._client is None:
            self._client = create_client(self.url, self.key)
        return self._client

    def ping(self, *, force: bool = False) -> bool:
        """Testa conectividade REST e inicialização do cliente Supabase."""
        if not self.is_configured:
            self._online = False
            self.last_error = "Configure SUPABASE_URL e SUPABASE_KEY no ambiente."
            return False

        if self._online is not None and not force:
            return self._online

        try:
            response = requests.get(
                f"{self.url}/rest/v1/",
                headers={"apikey": self.key, "Authorization": f"Bearer {self.key}"},
                timeout=8,
            )
            if response.status_code >= 500:
                self._online = False
                self.last_error = f"Supabase respondeu HTTP {response.status_code}."
                return False

            client = self.get_client()
            if client is None:
                self._online = False
                self.last_error = "Falha ao inicializar o cliente supabase-py."
                return False

            self._online = True
            self.last_error = ""
            return True
        except requests.RequestException as exc:
            self._online = False
            self.last_error = str(exc)
            return False
        except Exception as exc:  # pragma: no cover - erro inesperado do SDK
            self._online = False
            self.last_error = str(exc)
            return False

    def check_connectivity(self, *, force: bool = False) -> bool:
        return self.ping(force=force)

    @property
    def is_online(self) -> bool:
        return self.ping()

    def reset_cache(self) -> None:
        self._online = None
        self._client = None


def get_supabase() -> SupabaseClient:
    return SupabaseClient.instance()
