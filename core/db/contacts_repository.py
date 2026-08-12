"""Repositório de contatos."""

from __future__ import annotations

from datetime import datetime

from core.constants import AGATEK_ADDRESS
from core.db.connection import get_connection
from core.db.logs_repository import add_log
from utils.sanitization import sanitize_name, sanitize_phone, sanitize_text


def insert_contact(name: str, phone: str, address: str | None = None) -> bool:
    """Insere contato se não existir. Retorna True se inseriu."""
    clean_name = sanitize_name(name)
    clean_phone = sanitize_phone(phone)
    target_address = sanitize_text(address or AGATEK_ADDRESS)
    digits_phone = "".join(filter(str.isdigit, clean_phone))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    with get_connection() as conn:
        exists = conn.execute(
            """
            SELECT 1 FROM contacts
            WHERE name = ? OR (
                phone != '' AND REPLACE(REPLACE(REPLACE(REPLACE(phone, '(', ''), ')', ''), '-', ''), ' ', '') = ?
            )
            LIMIT 1
            """,
            (clean_name, digits_phone),
        ).fetchone()
        if exists:
            return False
        conn.execute(
            """
            INSERT INTO contacts (name, phone, address, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (clean_name, clean_phone, target_address, now_str),
        )
        conn.commit()
    return True


def import_contacts_batch(contacts: list[tuple[str, str]]) -> int:
    """Importa lote de contatos. Retorna quantidade inserida."""
    count = 0
    for name, phone in contacts:
        if insert_contact(name, phone):
            count += 1
    if count > 0:
        add_log("IMPORTAÇÃO", f"Importados {count} novos contatos da agenda (.VCF).")
    return count


def clear_all_contacts() -> None:
    """Remove todos os contatos."""
    with get_connection() as conn:
        conn.execute("DELETE FROM contacts")
        conn.commit()
    add_log("EXCLUSÃO", "Todos os contatos da agenda foram removidos.")


def search_contacts(query: str, limit: int = 3) -> list[dict]:
    """Busca contatos por nome."""
    clean_q = query.strip()
    if not clean_q or len(clean_q) < 2:
        return []
    with get_connection() as conn:
        conn.row_factory = _row_factory
        rows = conn.execute(
            """
            SELECT name AS reseller_name, phone, address FROM contacts
            WHERE name LIKE ?
            LIMIT ?
            """,
            (f"%{clean_q}%", limit),
        ).fetchall()
        return [dict(row) for row in rows]


def get_contact_by_name(name: str) -> dict | None:
    """Busca contato exato por nome."""
    clean_q = name.strip()
    if not clean_q:
        return None
    with get_connection() as conn:
        conn.row_factory = _row_factory
        row = conn.execute(
            "SELECT phone, address FROM contacts WHERE name LIKE ? LIMIT 1",
            (clean_q,),
        ).fetchone()
        return dict(row) if row else None


def _row_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
