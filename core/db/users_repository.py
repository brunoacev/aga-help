"""Repositório de usuários da aplicação (SQLite local)."""

from __future__ import annotations

from datetime import datetime

from core.db.connection import get_connection


def ensure_default_users(default_users: tuple[dict, ...], hash_fn) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        for user in default_users:
            handle = user["handle"]
            if not handle.startswith("@"):
                handle = f"@{handle}"
            exists = conn.execute(
                "SELECT 1 FROM app_users WHERE handle = ? LIMIT 1",
                (handle,),
            ).fetchone()
            if exists:
                continue
            conn.execute(
                """
                INSERT INTO app_users (name, handle, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user["name"], handle, hash_fn(user["password"]), now),
            )
        conn.commit()


def authenticate_local_user(handle: str, password: str, hash_fn) -> dict | None:
    password_hash = hash_fn(password)
    with get_connection() as conn:
        conn.row_factory = _row_factory
        row = conn.execute(
            """
            SELECT id, name, handle FROM app_users
            WHERE handle = ? AND password_hash = ?
            LIMIT 1
            """,
            (handle, password_hash),
        ).fetchone()
        return dict(row) if row else None


def upsert_user_remote(name: str, handle: str, password_hash: str) -> None:
    from core.supabase_client import get_supabase

    client = get_supabase().get_client()
    if not client:
        return
    try:
        existing = (
            client.table("app_users")
            .select("id")
            .eq("handle", handle)
            .limit(1)
            .execute()
        )
        payload = {
            "name": name,
            "handle": handle,
            "password_hash": password_hash,
        }
        if existing.data:
            client.table("app_users").update(payload).eq("handle", handle).execute()
        else:
            client.table("app_users").insert(payload).execute()
    except Exception:
        pass


def _row_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
