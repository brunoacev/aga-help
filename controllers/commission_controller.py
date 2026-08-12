"""Controller de comissões e métricas de faturamento."""

from __future__ import annotations

from datetime import datetime

from core.db.orders_repository import get_orders
from utils.formatting import format_brl
from utils.order_dates import parse_order_billing_date
from utils.period_filter import format_period_label, get_period_bounds, shift_reference_date

BILLED_STATUS = "Faturado"
DEFAULT_COMMISSION_RATE = 5.0


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
        try:
            value = float(clean)
        except ValueError:
            value = DEFAULT_COMMISSION_RATE
        self.commission_rate = max(0.0, min(value, 100.0))

    def shift_period(self, direction: int) -> None:
        self.reference_date = shift_reference_date(self.period, self.reference_date, direction)

    def _filter_billed_orders(self) -> list[dict]:
        start, end = get_period_bounds(self.period, self.reference_date)
        filtered: list[dict] = []
        for order in get_orders():
            if order.get("status") != BILLED_STATUS:
                continue
            billed_on = parse_order_billing_date(order)
            if billed_on is None:
                continue
            if start <= billed_on <= end:
                filtered.append(order)
        filtered.sort(key=lambda o: parse_order_billing_date(o) or datetime.min, reverse=True)
        return filtered

    def _commission_amount(self, value: float) -> float:
        return round(value * (self.commission_rate / 100.0), 2)

    def build_report(self) -> dict:
        """Monta KPIs e linhas da tabela de comissões."""
        orders = self._filter_billed_orders()
        start, end = get_period_bounds(self.period, self.reference_date)

        total_billed = sum(float(o.get("value") or 0) for o in orders)
        order_count = len(orders)
        avg_ticket = round(total_billed / order_count, 2) if order_count else 0.0
        total_commission = round(sum(self._commission_amount(float(o.get("value") or 0)) for o in orders), 2)

        rows: list[dict] = []
        for order in orders:
            value = float(order.get("value") or 0)
            commission = self._commission_amount(value)
            billed_on = parse_order_billing_date(order)
            rows.append(
                {
                    "date": billed_on.strftime("%d/%m/%Y") if billed_on else "—",
                    "order_number": order.get("order_number", "—"),
                    "client": order.get("reseller_name", "—"),
                    "total": value,
                    "total_fmt": format_brl(value),
                    "rate": self.commission_rate,
                    "commission": commission,
                    "commission_fmt": format_brl(commission),
                    "payment_status": order.get("payment_status") or "Pendente",
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
        }
