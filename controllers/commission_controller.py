"""Controller de comissões e métricas de faturamento."""

from __future__ import annotations

from datetime import datetime

from core.db.orders_repository import backfill_order_timestamps, get_orders
from utils.formatting import format_brl, safe_float
from utils.order_dates import format_order_datetime, normalize_order_created_at, resolve_order_billing_date
from utils.period_filter import format_period_label, get_period_bounds, shift_reference_date

BILLED_STATUS = "Faturado"
DEFAULT_COMMISSION_RATE = 5.0
DEFAULT_FALLBACK_DATE = "11/08/2026"
DEFAULT_FALLBACK_DATETIME = datetime(2026, 8, 11)


def _empty_report(controller: "CommissionController") -> dict:
    """Relatório zerado quando não há dados ou ocorre erro na consulta."""
    start, end = get_period_bounds(controller.period, controller.reference_date)
    zero = format_brl(0.0)
    return {
        "period_label": format_period_label(controller.period, start, end),
        "metrics": {
            "total_billed": 0.0,
            "total_billed_fmt": zero,
            "order_count": 0,
            "avg_ticket": 0.0,
            "avg_ticket_fmt": zero,
            "total_commission": 0.0,
            "total_commission_fmt": zero,
            "commission_rate": controller.commission_rate,
        },
        "rows": [],
        "error": True,
    }


class CommissionController:
    """Filtra pedidos faturados e calcula KPIs de comissão."""

    def __init__(self) -> None:
        self.period = "Mensal"
        self.reference_date = datetime.now()
        self.commission_rate = DEFAULT_COMMISSION_RATE

    def set_period(self, period: str) -> None:
        self.period = period or "Mensal"

    def set_commission_rate(self, rate_raw: str) -> None:
        clean = (rate_raw or "").strip().replace(",", ".")
        value = safe_float(clean) if clean else DEFAULT_COMMISSION_RATE
        self.commission_rate = max(0.0, min(value, 100.0))

    def shift_period(self, direction: int) -> None:
        self.reference_date = shift_reference_date(self.period, self.reference_date, direction)

    @staticmethod
    def order_value(order: dict) -> float:
        """Valor total do pedido com suporte a colunas legadas."""
        return safe_float(order.get("value") if order.get("value") is not None else order.get("total_price"))

    @staticmethod
    def normalize_order_fields(order: dict) -> dict:
        """Preenche campos ausentes para evitar quebra na UI."""
        normalized = normalize_order_created_at(dict(order))
        if not (normalized.get("created_at") or "").strip():
            normalized["created_at"] = DEFAULT_FALLBACK_DATE
        if normalized.get("value") is None and normalized.get("total_price") is None:
            normalized["value"] = 0.0
        elif normalized.get("value") is None:
            normalized["value"] = safe_float(normalized.get("total_price"))
        return normalized

    @staticmethod
    def is_commission_eligible(order: dict) -> bool:
        """Pedido concluído/faturado com valor registrado."""
        if order.get("status") != BILLED_STATUS:
            return False
        return CommissionController.order_value(order) >= 0.0

    def _filter_billed_orders(self) -> list[dict]:
        backfill_order_timestamps()
        start, end = get_period_bounds(self.period, self.reference_date)
        filtered: list[dict] = []
        for raw_order in get_orders():
            order = self.normalize_order_fields(raw_order)
            if not self.is_commission_eligible(order):
                continue
            billed_on = resolve_order_billing_date(order, fallback=DEFAULT_FALLBACK_DATETIME)
            if start <= billed_on <= end:
                filtered.append(order)
        filtered.sort(
            key=lambda o: resolve_order_billing_date(o, fallback=DEFAULT_FALLBACK_DATETIME),
            reverse=True,
        )
        return filtered

    def _commission_amount(self, value: float) -> float:
        return round(safe_float(value) * (self.commission_rate / 100.0), 2)

    def build_report(self) -> dict:
        """Monta KPIs e linhas da tabela de comissões."""
        try:
            orders = self._filter_billed_orders()
            start, end = get_period_bounds(self.period, self.reference_date)

            total_billed = sum(self.order_value(o) for o in orders)
            order_count = len(orders)
            avg_ticket = round(total_billed / order_count, 2) if order_count else 0.0
            total_commission = round(sum(self._commission_amount(self.order_value(o)) for o in orders), 2)

            rows: list[dict] = []
            for order in orders:
                value = self.order_value(order)
                commission = self._commission_amount(value)
                rows.append(
                    {
                        "date": format_order_datetime(order, billing=True),
                        "order_number": str(order.get("order_number") or "—"),
                        "client": str(order.get("reseller_name") or "—"),
                        "total": value,
                        "total_fmt": format_brl(value),
                        "rate": self.commission_rate,
                        "commission": commission,
                        "commission_fmt": format_brl(commission),
                        "payment_status": str(order.get("payment_status") or "Pendente"),
                        "status": str(order.get("status") or BILLED_STATUS),
                    }
                )

            return {
                "period_label": format_period_label(self.period, start, end),
                "metrics": {
                    "total_billed": total_billed,
                    "total_billed_fmt": format_brl(total_billed),
                    "order_count": order_count,
                    "avg_ticket": avg_ticket,
                    "avg_ticket_fmt": format_brl(avg_ticket),
                    "total_commission": total_commission,
                    "total_commission_fmt": format_brl(total_commission),
                    "commission_rate": self.commission_rate,
                },
                "rows": rows,
                "error": False,
            }
        except Exception:
            return _empty_report(self)
