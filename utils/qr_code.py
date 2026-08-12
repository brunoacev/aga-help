"""Geração de QR Code em Base64 para renderização no Flet."""

from __future__ import annotations

import base64
import io

import qrcode


def generate_qr_base64(qr_data_string: str) -> str:
    """Converte uma string em PNG Base64 (use com `ft.Image(src=f'data:image/png;base64,{...}')`)."""
    payload = (qr_data_string or "").strip() or "aga-help-whatsapp"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def qr_data_uri(qr_data_string: str) -> str:
    """Retorna data URI pronto para `ft.Image(src=...)`."""
    return f"data:image/png;base64,{generate_qr_base64(qr_data_string)}"
