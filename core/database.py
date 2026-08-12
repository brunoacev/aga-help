"""
Facade de compatibilidade — reexporta APIs públicas do módulo de dados.
Preferir imports diretos de core.db.* e core.services.* em código novo.
"""

from core.constants import AGATEK_ADDRESS
from core.db.orders_repository import add_order
from core.db.schema import init_db
from core.db.logs_repository import get_logs
from core.services.contact_service import (
    clear_all_contacts,
    get_profile_by_exact_name,
    search_reseller_profiles,
)
from core.services.order_service import (
    clear_all_orders,
    delete_order,
    get_orders,
    update_order_status,
)


def import_vcf_contacts(vcf_text: str) -> int:
    """Importa VCF; retorna quantidade inserida (compatibilidade)."""
    from core.services.contact_service import import_vcf_contacts as _import

    count, _error = _import(vcf_text)
    return count


__all__ = [
    "AGATEK_ADDRESS",
    "init_db",
    "get_logs",
    "clear_all_contacts",
    "get_profile_by_exact_name",
    "import_vcf_contacts",
    "search_reseller_profiles",
    "clear_all_orders",
    "delete_order",
    "get_orders",
    "update_order_status",
    "add_order",
]
