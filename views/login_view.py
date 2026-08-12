"""Tela de login da aplicação."""

from __future__ import annotations

import flet as ft

from core import colors
from core.auth.auth_service import authenticate, bootstrap_users
from core.auth.user_session import set_user
from core.supabase_client import get_supabase
from utils.flet_compat import get_alignment_center, make_padding_symmetric, show_snackbar
from utils.ui_theme import FONT_BODY, FONT_CAPTION, RADIUS, S4, field_style, make_primary_button, text_section_heading


class LoginView(ft.Container):
    """Autenticação com usuários @suporte e @rota."""

    def __init__(self, page: ft.Page, on_success):
        self.app_page = page
        self.on_success = on_success
        bootstrap_users()

        self.txt_handle = ft.TextField(
            label="Usuário",
            hint_text="suporte ou rota (com ou sem @)",
            autofocus=True,
            on_submit=self._login,
            **field_style(),
        )
        self.txt_password = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            on_submit=self._login,
            **field_style(),
        )
        self.lbl_status = ft.Text("", size=FONT_CAPTION, color=colors.WA_LIST_PREVIEW, visible=False)

        supabase = get_supabase()
        if not supabase.is_configured:
            self.lbl_status.value = (
                "Modo offline/local: configure SUPABASE_URL e SUPABASE_KEY para sincronizar com a nuvem."
            )
            self.lbl_status.color = colors.COLOR_ORCAMENTO
            self.lbl_status.visible = True
        elif not supabase.is_online:
            self.lbl_status.value = (
                "Sem conexão com o Supabase. Login local disponível; histórico será salvo offline."
            )
            self.lbl_status.color = colors.COLOR_ORCAMENTO
            self.lbl_status.visible = True

        card = ft.Container(
            width=420,
            bgcolor=colors.WA_PANEL_BG,
            border_radius=RADIUS,
            padding=S4,
            content=ft.Column(
                [
                    text_section_heading("AGA HELP"),
                    ft.Text(
                        "Entre com seu usuário para registrar ações no Kanban.",
                        size=FONT_CAPTION,
                        color=colors.WA_LIST_PREVIEW,
                    ),
                    self.txt_handle,
                    self.txt_password,
                    self.lbl_status,
                    make_primary_button("Entrar", self._login, height=44),
                    ft.Text(
                        "Usuários: @suporte / @rota — senha: 123",
                        size=10,
                        color=colors.WA_META_INCOMING,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                spacing=16,
                tight=True,
            ),
        )

        super().__init__(
            expand=True,
            bgcolor=colors.BG_PRIMARY,
            alignment=get_alignment_center(),
            content=card,
        )

    def _login(self, _e=None) -> None:
        handle_raw = (self.txt_handle.value or "").strip()
        handle = handle_raw if handle_raw.startswith("@") else f"@{handle_raw.lstrip('@')}"
        password = (self.txt_password.value or "").strip()
        user, error = authenticate(handle, password)
        if not user:
            show_snackbar(self.app_page, error or "Falha na autenticação.", success=False)
            return
        set_user(self.app_page, user)
        self.on_success(user)
