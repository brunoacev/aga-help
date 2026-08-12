"""Serviço de contatos e importação VCF."""

from __future__ import annotations

from core.constants import AGATEK_ADDRESS
from core.db import contacts_repository
from core.db.orders_repository import get_order_profile_by_name, search_orders_by_reseller
from core.services.vcf_parser import parse_vcf_content
from utils.sanitization import validate_vcf_input


def import_vcf_contacts(vcf_text: str) -> tuple[int, str]:
    """
    Importa contatos de texto VCF.
    Retorna (quantidade_inserida, mensagem_erro ou vazio).
    """
    valid, error = validate_vcf_input(vcf_text)
    if not valid:
        return 0, error

    contacts = parse_vcf_content(vcf_text)
    if not contacts:
        return 0, "Nenhum contato válido encontrado no VCF."

    count = contacts_repository.import_contacts_batch(contacts)
    return count, ""


def search_reseller_profiles(query: str, limit: int = 3) -> list[dict]:
    """Busca revendas em contatos e pedidos, deduplicando por nome."""
    contact_results = contacts_repository.search_contacts(query, limit=limit)
    order_rows = search_orders_by_reseller(query, limit=limit)
    order_results = [
        {
            "reseller_name": row["reseller_name"],
            "phone": row.get("phone", ""),
            "address": row.get("address", AGATEK_ADDRESS),
        }
        for row in order_rows
    ]

    merged: list[dict] = []
    seen_names: set[str] = set()
    for profile in contact_results + order_results:
        name = profile.get("reseller_name", "")
        key = name.lower()
        if key and key not in seen_names:
            seen_names.add(key)
            merged.append(profile)
        if len(merged) >= limit:
            break
    return merged


def get_profile_by_exact_name(reseller_name: str) -> dict | None:
    """Retorna perfil de revenda a partir de contatos ou pedidos."""
    profile = contacts_repository.get_contact_by_name(reseller_name)
    if profile:
        return profile
    return get_order_profile_by_name(reseller_name)


def clear_all_contacts() -> None:
    """Remove todos os contatos."""
    contacts_repository.clear_all_contacts()


def list_agenda_contacts(query: str = "", *, limit: int = 500) -> list[dict]:
    """Lista contatos da agenda para exibição na view, com busca opcional."""
    return contacts_repository.list_contacts(query, limit=limit)
