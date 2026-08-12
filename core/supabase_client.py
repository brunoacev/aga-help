"""Cliente Supabase com verificação de conectividade e fallback local."""

from __future__ import annotations

import os
from typing import Any

import requests

try:
    from supabase import Client, create_client
except ImportError:  # pragma: no cover - dependência opcional em runtime mínimo
    Client = Any  # type: ignore[misc, assignment]
    create_client = None  # type: ignore[assignment]


class SupabaseClient:
    """Singleton leve para acesso ao Supabase via REST."""

    _instance: SupabaseClient | None = None

    def __init__(self) -> None:
        self.url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
        self.key = (
            os.getenv("SUPABASE_KEY", "").strip()
            or os.getenv("SUPABASE_ANON_KEY", "").strip()
        )
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

    def check_connectivity(self, *, force: bool = False) -> bool:
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
                timeout=6,
            )
            self._online = response.status_code < 500
            if not self._online:
                self.last_error = f"Supabase respondeu HTTP {response.status_code}."
            else:
                self.last_error = ""
            return self._online
        except requests.RequestException as exc:
            self._online = False
            self.last_error = str(exc)
            return False

    @property
    def is_online(self) -> bool:
        return self.check_connectivity()

    def reset_cache(self) -> None:
        self._online = None
        self._client = None


def get_supabase() -> SupabaseClient:
    return SupabaseClient.instance()
