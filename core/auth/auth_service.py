"""Autenticação de usuários da aplicação (local + Supabase)."""

from __future__ import annotations

import hashlib
from datetime import datetime

from core.db.users_repository import authenticate_local_user, ensure_default_users, upsert_user_remote
from core.supabase_client import get_supabase

DEFAULT_USERS = (
    {"name": "Suporte", "handle": "@suporte", "password": "123"},
    {"name": "Rota", "handle": "@rota", "password": "123"},
)


def hash_password(password: str) -> str:
    raw = f"aga-help:{password}".encode()
    return hashlib.sha256(raw).hexdigest()


def normalize_handle(handle: str) -> str:
    clean = (handle or "").strip().lower()
    if not clean:
        return ""
    return clean if clean.startswith("@") else f"@{clean}"


def bootstrap_users() -> None:
    """Garante usuários padrão no SQLite local e tenta replicar no Supabase."""
    ensure_default_users(DEFAULT_USERS, hash_password)
    supabase = get_supabase()
    if supabase.is_online:
        for user in DEFAULT_USERS:
            upsert_user_remote(
                name=user["name"],
                handle=normalize_handle(user["handle"]),
                password_hash=hash_password(user["password"]),
            )


def authenticate(handle: str, password: str) -> tuple[dict | None, str]:
    """Autentica usuário. Retorna (user_dict, erro)."""
    normalized = normalize_handle(handle)
    if not normalized or not password:
        return None, "Informe usuário e senha."

    user = authenticate_local_user(normalized, password, hash_password)
    if user:
        return user, ""

    supabase = get_supabase()
    if not supabase.is_configured:
        return None, "Usuário ou senha inválidos."
    if not supabase.is_online:
        return None, "Sem conexão com o banco online. Verifique a internet."

    return None, "Usuário ou senha inválidos."


def format_login_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
