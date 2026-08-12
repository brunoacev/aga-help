"""Sessão do usuário logado (espelhada em page.session via store dedicado)."""

from __future__ import annotations

from typing import Any

import flet as ft

SESSION_STORE_KEY = "aga_auth_user"


def set_user(page: ft.Page, user: dict[str, Any]) -> None:
    """Persiste usuário autenticado na sessão da página."""
    store = getattr(page, "_aga_session_store", None)
    if store is None:
        store = {}
        page._aga_session_store = store  # type: ignore[attr-defined]
    store[SESSION_STORE_KEY] = dict(user)
    if hasattr(page, "session") and hasattr(page.session, "index"):
        page.session.index[SESSION_STORE_KEY] = dict(user)  # type: ignore[index]


def get_user(page: ft.Page | None) -> dict[str, Any] | None:
    if not page:
        return None
    store = getattr(page, "_aga_session_store", {})
    user = store.get(SESSION_STORE_KEY)
    if user:
        return dict(user)
    if hasattr(page, "session") and hasattr(page.session, "index"):
        cached = page.session.index.get(SESSION_STORE_KEY)  # type: ignore[index]
        if cached:
            return dict(cached)
    return None


def get_user_handle(page: ft.Page | None) -> str:
    user = get_user(page)
    if not user:
        return ""
    return str(user.get("handle") or "")


def clear_user(page: ft.Page) -> None:
    store = getattr(page, "_aga_session_store", None)
    if isinstance(store, dict):
        store.pop(SESSION_STORE_KEY, None)
    if hasattr(page, "session") and hasattr(page.session, "index"):
        page.session.index.pop(SESSION_STORE_KEY, None)  # type: ignore[index]
