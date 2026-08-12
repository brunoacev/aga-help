"""Testes do controller de comissões."""

from datetime import datetime
from unittest.mock import patch

from controllers.commission_controller import CommissionController


def test_build_report_empty():
    controller = CommissionController()
    with patch("controllers.commission_controller.get_orders", return_value=[]):
        report = controller.build_report()
    assert report["metrics"]["order_count"] == 0
    assert report["rows"] == []


def test_build_report_calculates_commission():
    controller = CommissionController()
    controller.commission_rate = 10.0
    controller.reference_date = datetime(2026, 8, 15)
    controller.period = "Mensal"
    orders = [
        {
            "status": "Faturado",
            "value": 1000.0,
            "order_number": "100",
            "reseller_name": "Revenda A",
            "billed_at": "2026-08-10 14:30:00",
            "payment_status": "Pendente",
        }
    ]
    with patch("controllers.commission_controller.get_orders", return_value=orders):
        report = controller.build_report()
    assert report["metrics"]["order_count"] == 1
    assert report["metrics"]["total_billed"] == 1000.0
    assert report["metrics"]["total_commission"] == 100.0
    assert report["rows"][0]["commission"] == 100.0


def test_legacy_order_without_date_uses_fallback():
    controller = CommissionController()
    controller.reference_date = datetime(2026, 8, 11)
    controller.period = "Diário"
    orders = [
        {
            "status": "Faturado",
            "value": 500.0,
            "order_number": "200",
            "reseller_name": "Revenda B",
            "payment_status": "Pendente",
        }
    ]
    with patch("controllers.commission_controller.get_orders", return_value=orders):
        report = controller.build_report()
    assert report["metrics"]["order_count"] == 1
    assert report["rows"][0]["total"] == 500.0
