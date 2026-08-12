"""Seção de identificação da revenda."""

from __future__ import annotations

import flet as ft

from core import colors
from utils.flet_compat import border_all, safe_update
from utils.ui_theme import COL_QUARTER, COL_THIRD, RADIUS, S3, clickable_tile, section_card, text_body


class ResellerSection(ft.Container):
    """Campos de revenda com autocomplete."""

    def __init__(self, input_style: dict, readonly_style: dict):
        self._is_updating = False
        self.on_reseller_change = None
        self.on_profile_select = None

        self.txt_reseller = ft.TextField(
            label="Nome da Revenda *",
            on_change=self._handle_change,
            **input_style,
        )
        self.txt_phone = ft.TextField(
            label="Telefone (Auto)",
            hint_text="Aguardando revenda...",
            **readonly_style,
        )
        self.txt_address = ft.TextField(
            label="Endereço de Entrega (Auto)",
            hint_text="Aguardando revenda...",
            **readonly_style,
        )

        self.suggestions_box = ft.Column(spacing=S3)
        self.suggestions_container = ft.Container(
            content=self.suggestions_box,
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all(colors.BORDER_FOCUS),
            border_radius=RADIUS,
            padding=S3,
            visible=False,
        )

        form_row = ft.ResponsiveRow(
            [
                ft.Container(self.txt_reseller, col=COL_THIRD),
                ft.Container(self.txt_phone, col=COL_QUARTER),
                ft.Container(self.txt_address, col={"sm": 12, "md": 6, "lg": 5, "xl": 5}),
            ],
            run_spacing=S3,
            spacing=S3,
        )

        card = section_card(
            "1. Identificação da Revenda",
            ft.Column([form_row, self.suggestions_container], spacing=S3),
        )
        super().__init__(
            bgcolor=card.bgcolor,
            border=card.border,
            border_radius=card.border_radius,
            padding=card.padding,
            content=card.content,
        )

    def _handle_change(self, _e):
        if self._is_updating or not self.on_reseller_change:
            return
        name = (self.txt_reseller.value or "").strip()
        result = self.on_reseller_change(name)
        self.txt_phone.value = result.get("phone", "")
        self.txt_address.value = result.get("address", "")
        self._render_suggestions(result.get("suggestions", []))
        safe_update(self)

    def _render_suggestions(self, profiles: list[dict]) -> None:
        self.suggestions_box.controls.clear()
        if not profiles:
            self.suggestions_container.visible = False
            return

        for profile in profiles:
            p_name = profile["reseller_name"]
            p_phone = profile.get("phone", "")
            p_addr = profile.get("address", "")

            row_content = ft.Row(
                [
                    text_body(f"🏢 {p_name}", weight=ft.FontWeight.W_600),
                    text_body(p_addr, color=colors.TEXT_MUTED, overflow=ft.TextOverflow.ELLIPSIS),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            item = clickable_tile(
                row_content,
                lambda e, n=p_name, p=p_phone, a=p_addr: self.select_profile(n, p, a),
            )
            self.suggestions_box.controls.append(item)
        self.suggestions_container.visible = True

    def select_profile(self, reseller_name: str, phone: str, address: str) -> None:
        """Preenche campos com perfil selecionado."""
        self._is_updating = True
        self.txt_reseller.value = reseller_name
        self.txt_phone.value = phone
        self.txt_address.value = address
        self.suggestions_container.visible = False
        safe_update(self)
        self._is_updating = False
        if self.on_profile_select:
            self.on_profile_select()

    def hide_suggestions(self) -> None:
        self.suggestions_container.visible = False

    def get_values(self) -> dict:
        return {
            "reseller_name": (self.txt_reseller.value or "").strip(),
            "phone": self.txt_phone.value or "",
            "address": self.txt_address.value or "",
        }

    def reset(self) -> None:
        self._is_updating = True
        self.txt_reseller.value = ""
        self.txt_phone.value = ""
        self.txt_address.value = ""
        self.suggestions_container.visible = False
        self._is_updating = False

    def mark_invalid(self) -> None:
        self.txt_reseller.border_color = colors.ERROR

    def clear_validation(self) -> None:
        self.txt_reseller.border_color = colors.BORDER_COLOR
