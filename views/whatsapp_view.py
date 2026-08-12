"""View de atendimento WhatsApp com autenticação por QR Code."""

from __future__ import annotations

import flet as ft

from controllers.whatsapp_controller import WhatsAppController, WhatsAppConversation
from core import colors
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric
from utils.qr_code import generate_qr_base64
from utils.ui_theme import FONT_BODY, FONT_CAPTION, RADIUS, S1, S2, S3, S4, page_header, text_caption, text_section_heading

QR_INSTRUCTIONS = (
    "Abra o WhatsApp > Aparelhos conectados > Conectar um aparelho"
)
LEFT_PANEL_WIDTH = 340


class WhatsAppView(ft.Container):
    """Painel de conversas e chat com fluxo de conexão via QR Code."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        self.controller = WhatsAppController()
        self.border_all = border_all(colors.BORDER_COLOR)
        self.selected_conversation_id: str | None = None

        self.qr_image = ft.Image(
            src=self._build_qr_src(self.controller.session_token),
            width=200,
            height=200,
            fit=ft.BoxFit.CONTAIN,
            border_radius=RADIUS,
        )
        self.lbl_connection_status = ft.Text(
            "Desconectado",
            size=FONT_CAPTION,
            color=colors.ERROR,
            weight=ft.FontWeight.W_600,
        )
        self.qr_panel = ft.Column(
            [
                ft.Container(content=self.qr_image, alignment=get_alignment_center()),
                ft.Text(QR_INSTRUCTIONS, size=FONT_CAPTION, color=colors.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                ft.Button(
                    content="Gerar Novo QrCode",
                    icon=getattr(ft.Icons, "QR_CODE_SCANNER", None) or "qr_code_scanner",
                    bgcolor=colors.PRIMARY,
                    color=colors.TEXT_PRIMARY,
                    on_click=self._on_generate_qr,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=S3,
            visible=True,
        )
        self.lbl_connected_badge = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(getattr(ft.Icons, "CHECK_CIRCLE", None) or "check_circle", color=colors.SUCCESS, size=18),
                    ft.Text("", size=FONT_BODY, color=colors.SUCCESS, weight=ft.FontWeight.W_600),
                ],
                spacing=S2,
            ),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all(colors.SUCCESS),
            border_radius=RADIUS,
            padding=make_padding_symmetric(horizontal=S3, vertical=S2),
            visible=False,
        )
        self.connected_panel = ft.Column(
            [
                self.lbl_connected_badge,
                ft.OutlinedButton(
                    content="Desconectar",
                    icon=getattr(ft.Icons, "LOGOUT", None) or "logout",
                    on_click=self._on_disconnect,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=S3,
            visible=False,
        )

        self.conversations_column = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)
        self.chat_header = ft.Text("Selecione uma conversa", size=FONT_BODY, color=colors.TEXT_PRIMARY, weight=ft.FontWeight.W_600)
        self.messages_column = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)
        self.chat_empty_hint = text_caption("Nenhuma conversa selecionada.")

        left_panel = ft.Container(
            width=LEFT_PANEL_WIDTH,
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S4,
            content=ft.Column(
                [
                    text_section_heading("Status da Conexão"),
                    self.lbl_connection_status,
                    self.qr_panel,
                    self.connected_panel,
                    ft.Divider(height=1, color=colors.BORDER_COLOR),
                    text_section_heading("Conversas Ativas"),
                    ft.Container(content=self.conversations_column, expand=True),
                ],
                spacing=S3,
                expand=True,
            ),
        )

        right_panel = ft.Container(
            expand=True,
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S4,
            content=ft.Column(
                [
                    self.chat_header,
                    ft.Divider(height=1, color=colors.BORDER_COLOR),
                    ft.Container(content=self.messages_column, expand=True),
                    self.chat_empty_hint,
                ],
                spacing=S3,
                expand=True,
            ),
        )

        super().__init__(
            expand=True,
            bgcolor=colors.BG_PRIMARY,
            padding=make_padding_symmetric(horizontal=S4, vertical=S4),
            content=ft.Column(
                [
                    page_header(
                        "WhatsApp / Conversas",
                        "Central de atendimento e histórico de mensagens.",
                    ),
                    ft.Row(
                        [left_panel, right_panel],
                        spacing=S4,
                        expand=True,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    ),
                ],
                spacing=S4,
                expand=True,
            ),
        )

        self._load_conversations()
        self._refresh_qr_image()
        self._update_connection_ui()

    def did_mount(self) -> None:
        """Garante QR Code renderizado após montagem na página."""
        self._refresh_qr_image()
        self._update_connection_ui()
        if self.app_page:
            self.app_page.update()

    def _build_qr_src(self, token: str) -> str:
        return f"data:image/png;base64,{generate_qr_base64(token)}"

    def _refresh_qr_image(self) -> None:
        self.qr_image.src = self._build_qr_src(self.controller.session_token)

    def _update_connection_ui(self) -> None:
        connected = self.controller.connected
        self.lbl_connection_status.value = "Conectado" if connected else "Desconectado"
        self.lbl_connection_status.color = colors.SUCCESS if connected else colors.ERROR
        self.qr_panel.visible = not connected
        self.connected_panel.visible = connected
        if connected:
            phone = self.controller.connected_phone
            self.lbl_connected_badge.content.controls[1].value = f"Conectado como {phone}"

    def _load_conversations(self) -> None:
        self.conversations_column.controls.clear()
        for conversation in self.controller.list_conversations():
            self.conversations_column.controls.append(self._build_conversation_tile(conversation))
        if self.controller.list_conversations() and self.selected_conversation_id is None:
            self._select_conversation(self.controller.list_conversations()[0].id)

    def _build_conversation_tile(self, conversation: WhatsAppConversation) -> ft.Container:
        is_active = conversation.id == self.selected_conversation_id
        unread_badge = (
            ft.Container(
                content=ft.Text(str(conversation.unread), size=10, color=colors.TEXT_PRIMARY),
                bgcolor=colors.PRIMARY,
                border_radius=10,
                padding=make_padding_symmetric(horizontal=6, vertical=2),
            )
            if conversation.unread
            else None
        )
        trailing = [unread_badge] if unread_badge else []
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(conversation.name, size=FONT_BODY, weight=ft.FontWeight.W_600, color=colors.TEXT_PRIMARY),
                            ft.Text(conversation.last_message, size=FONT_CAPTION, color=colors.TEXT_MUTED, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=S1,
                        expand=True,
                    ),
                    *trailing,
                ],
                spacing=S2,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=make_padding_symmetric(horizontal=S3, vertical=S2),
            border_radius=RADIUS,
            bgcolor=colors.BG_SURFACE_LIGHT if is_active else colors.BG_SURFACE,
            border=border_all(colors.PRIMARY if is_active else colors.BORDER_COLOR),
            ink=True,
            on_click=lambda _, cid=conversation.id: self._select_conversation(cid),
        )

    def _build_message_bubble(self, message) -> ft.Container:
        bubble_color = colors.PRIMARY if message.from_me else colors.BG_SURFACE_LIGHT
        text_color = colors.TEXT_PRIMARY
        alignment = ft.MainAxisAlignment.END if message.from_me else ft.MainAxisAlignment.START
        return ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(message.text, size=FONT_BODY, color=text_color),
                            ft.Text(message.time, size=10, color=colors.TEXT_MUTED),
                        ],
                        spacing=S1,
                        tight=True,
                    ),
                    bgcolor=bubble_color,
                    border_radius=RADIUS,
                    padding=make_padding_symmetric(horizontal=S3, vertical=S2),
                    width=320,
                ),
            ],
            alignment=alignment,
        )

    def _select_conversation(self, conversation_id: str) -> None:
        self.selected_conversation_id = conversation_id
        conversation = next(
            (item for item in self.controller.list_conversations() if item.id == conversation_id),
            None,
        )
        if not conversation:
            return

        self.chat_header.value = f"{conversation.name} · {conversation.phone}"
        self.messages_column.controls.clear()
        messages = self.controller.get_messages(conversation_id)
        self.chat_empty_hint.visible = not messages
        for message in messages:
            self.messages_column.controls.append(self._build_message_bubble(message))

        self._load_conversations()
        if self.app_page:
            self.app_page.update()

    def _on_generate_qr(self, _e) -> None:
        self.controller.refresh_session_token()
        self._refresh_qr_image()
        self._update_connection_ui()
        if self.app_page:
            self.app_page.update()

    def _on_disconnect(self, _e) -> None:
        self.controller.disconnect()
        self._refresh_qr_image()
        self._update_connection_ui()
        if self.app_page:
            self.app_page.update()

    def simulate_connection(self, phone: str | None = None) -> None:
        """Atalho de demo para validar o estado conectado na UI."""
        self.controller.connect(phone)
        self._update_connection_ui()
        if self.app_page:
            self.app_page.update()
