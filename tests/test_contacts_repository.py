"""Testes de listagem de contatos da agenda."""

from __future__ import annotations

from core.db.contacts_repository import insert_contact, list_contacts


def test_list_contacts_returns_inserted_contact():
    insert_contact("Revenda Teste Lista", "(85) 99999-0000")
    results = list_contacts("Revenda Teste Lista")
    assert any(row["name"] == "Revenda Teste Lista" for row in results)


def test_list_contacts_empty_query_returns_all():
    insert_contact("Outro Contato", "(85) 98888-1111")
    results = list_contacts("")
    assert len(results) >= 1
