"""View de atendimento WhatsApp com autenticação por QR Code."""

from __future__ import annotations

import asyncio

import flet as ft

from controllers.whatsapp_controller import (
    STATUS_CONNECTED,
    STATUS_DISCONNECTED,
    STATUS_QR_READY,
    WhatsAppController,
    WhatsAppConversation,
)
from core import colors
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric, show_snackbar
from utils.ui_theme import FONT_BODY, FONT_CAPTION, RADIUS, S1, S2, S3, S4, field_style, page_header, text_caption, text_section_heading

QR_INSTRUCTIONS = "Abra o WhatsApp > Aparelhos conectados > Conectar um aparelho"
NODE_DOWNLOAD_URL = "https://nodejs.org/"
LEFT_PANEL_WIDTH = 340
POLL_INTERVAL_SECONDS = 2


class WhatsAppView(ft.Container):
    """Painel de conversas e chat com ponte local Baileys."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        self.controller = WhatsAppController()
        self.border_all = border_all(colors.BORDER_COLOR)
        self.selected_conversation_id: str | None = None
        self._polling = False
        self._last_status = STATUS_DISCONNECTED
        self._last_qr_src = ""

        self.node_alert = ft.Container(
            visible=False,
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all(colors.ERROR),
            border_radius=RADIUS,
            padding=S4,
            content=ft.Column(
                [
                    ft.Text(
                        "Node.js não encontrado",
                        size=FONT_BODY,
                        color=colors.ERROR,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Text(
                        "Instale o Node.js LTS para habilitar o WhatsApp real.",
                        size=FONT_CAPTION,
                        color=colors.TEXT_SECONDARY,
                    ),
                    ft.TextButton(
                        content="Baixar Node.js",
                        url=NODE_DOWNLOAD_URL,
                    ),
                ],
                spacing=S2,
                tight=True,
            ),
        )

        self.qr_image = ft.Image(
            src="",
            width=220,
            height=220,
            fit=ft.BoxFit.CONTAIN,
            border_radius=RADIUS,
            visible=False,
        )
        self.lbl_connection_status = ft.Text(
            "Iniciando ponte...",
            size=FONT_CAPTION,
            color=colors.TEXT_MUTED,
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
        self.chat_header = ft.Text(
            "Selecione uma conversa",
            size=FONT_BODY,
            color=colors.TEXT_PRIMARY,
            weight=ft.FontWeight.W_600,
        )
        self.messages_column = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)
        self.chat_empty_hint = text_caption("Nenhuma conversa selecionada.")
        self.txt_message = ft.TextField(
            label="Mensagem",
            hint_text="Digite sua resposta...",
            expand=True,
            multiline=False,
            disabled=True,
            on_submit=self._on_send_message,
            **field_style(),
        )
        self.btn_send = ft.Button(
            content="Enviar",
            icon=getattr(ft.Icons, "SEND_ROUNDED", None) or "send",
            bgcolor=colors.PRIMARY,
            color=colors.TEXT_PRIMARY,
            disabled=True,
            on_click=self._on_send_message,
        )
        self.compose_row = ft.Row(
            [self.txt_message, self.btn_send],
            spacing=S2,
            vertical_alignment=ft.CrossAxisAlignment.END,
        )

        left_panel = ft.Container(
            width=LEFT_PANEL_WIDTH,
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S4,
            content=ft.Column(
                [
                    text_section_heading("Status da Conexão"),
                    self.node_alert,
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
                    self.compose_row,
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
                        "Conexão real via ponte local (Baileys) — leia o QR Code no celular.",
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

    def on_show(self) -> None:
        """Inicia ponte e polling ao navegar para esta view."""
        self._polling = True
        if self.app_page:
            self.app_page.run_task(self._poll_connection_loop)

    def will_unmount(self) -> None:
        self._polling = False

    async def _poll_connection_loop(self) -> None:
        if not self.controller.node_available:
            self._show_node_missing()
            self._render_page()
            return

        started, error = self.controller.ensure_bridge_started()
        if not started:
            self.lbl_connection_status.value = error or "Falha ao iniciar ponte WhatsApp."
            self.lbl_connection_status.color = colors.ERROR
            self._render_page()
            return

        while self._polling:
            status = self.controller.get_connection_status()
            self._last_status = status

            if status == STATUS_QR_READY:
                qr_src = self.controller.fetch_qr_image_src()
                if qr_src and qr_src != self._last_qr_src:
                    self._last_qr_src = qr_src
                    self.qr_image.src = qr_src
                    self.qr_image.visible = True
                self._set_status_label("Aguardando leitura do QR Code", colors.COLOR_ORCAMENTO)
                self.qr_panel.visible = True
                self.connected_panel.visible = False
                self._set_compose_enabled(False)
            elif status == STATUS_CONNECTED:
                phone = self.controller.connected_phone or "WhatsApp"
                self.lbl_connected_badge.content.controls[1].value = f"Conectado como {phone}"
                self.qr_panel.visible = False
                self.connected_panel.visible = True
                self.qr_image.visible = False
                self._set_status_label("Conectado", colors.SUCCESS)
                self._set_compose_enabled(bool(self.selected_conversation_id))
                self._load_conversations()
                if self.selected_conversation_id:
                    self._refresh_messages(self.selected_conversation_id, update=False)
            else:
                self._set_status_label("Desconectado", colors.ERROR)
                self.qr_panel.visible = True
                self.connected_panel.visible = False
                self.qr_image.visible = bool(self._last_qr_src)
                self._set_compose_enabled(False)

            self._render_page()
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    def _show_node_missing(self) -> None:
        self.node_alert.visible = True
        self.lbl_connection_status.value = "Node.js necessário para conexão WhatsApp."
        self.lbl_connection_status.color = colors.ERROR
        self.qr_panel.visible = False
        self.connected_panel.visible = False

    def _set_status_label(self, text: str, color: str) -> None:
        self.lbl_connection_status.value = text
        self.lbl_connection_status.color = color

    def _set_compose_enabled(self, enabled: bool) -> None:
        self.txt_message.disabled = not enabled
        self.btn_send.disabled = not enabled

    def _render_page(self) -> None:
        if self.app_page:
            self.app_page.update()

    def _render_conversation_list(self) -> None:
        """Atualiza apenas os tiles da lista lateral (sem re-selecionar chat)."""
        conversations = self.controller.list_conversations()
        self.conversations_column.controls.clear()
        if not conversations:
            self.conversations_column.controls.append(
                text_caption("Nenhuma conversa encontrada ainda.")
            )
            return
        for conversation in conversations:
            self.conversations_column.controls.append(self._build_conversation_tile(conversation))

    def _load_conversations(self) -> None:
        conversations = self.controller.list_conversations()
        self._render_conversation_list()

        if not conversations:
            self.selected_conversation_id = None
            self.chat_empty_hint.visible = True
            self._set_compose_enabled(False)
            return

        valid_ids = {item.id for item in conversations}
        if self.selected_conversation_id not in valid_ids:
            self._select_conversation(conversations[0].id, update=False)

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
                            ft.Text(
                                conversation.name,
                                size=FONT_BODY,
                                weight=ft.FontWeight.W_600,
                                color=colors.TEXT_PRIMARY,
                            ),
                            ft.Text(
                                conversation.last_message,
                                size=FONT_CAPTION,
                                color=colors.TEXT_MUTED,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
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

    def _build_message_bubble(self, message) -> ft.Row:
        bubble_color = colors.PRIMARY if message.from_me else colors.BG_SURFACE_LIGHT
        alignment = ft.MainAxisAlignment.END if message.from_me else ft.MainAxisAlignment.START
        return ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(message.text, size=FONT_BODY, color=colors.TEXT_PRIMARY),
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

    def _select_conversation(self, conversation_id: str, *, update: bool = True) -> None:
        self.selected_conversation_id = conversation_id
        conversation = next(
            (item for item in self.controller.list_conversations() if item.id == conversation_id),
            None,
        )
        if not conversation:
            return

        self.chat_header.value = f"{conversation.name} · {conversation.phone}"
        self._refresh_messages(conversation_id, update=False)
        self.chat_empty_hint.visible = not self.messages_column.controls
        self._set_compose_enabled(self._last_status == STATUS_CONNECTED)
        self._render_conversation_list()
        if update:
            self._render_page()

    def _refresh_messages(self, conversation_id: str, *, update: bool = True) -> None:
        self.messages_column.controls.clear()
        for message in self.controller.get_messages(conversation_id):
            self.messages_column.controls.append(self._build_message_bubble(message))
        self.chat_empty_hint.visible = not self.messages_column.controls
        if update:
            self._render_page()

    def _on_send_message(self, _e) -> None:
        if not self.selected_conversation_id:
            show_snackbar(self.app_page, "Selecione uma conversa.", success=False)
            return
        text = (self.txt_message.value or "").strip()
        ok, error = self.controller.send_message(self.selected_conversation_id, text)
        if not ok:
            show_snackbar(self.app_page, error or "Não foi possível enviar.", success=False)
            return
        self.txt_message.value = ""
        self._refresh_messages(self.selected_conversation_id, update=False)
        self._render_conversation_list()
        self._render_page()

    def _on_generate_qr(self, _e) -> None:
        ok, error = self.controller.regenerate_qr()
        if not ok:
            show_snackbar(self.app_page, error or "Falha ao gerar QR Code.", success=False)
            return
        self._last_qr_src = ""
        show_snackbar(self.app_page, "Novo QR Code solicitado.", success=True)
        self._render_page()

    def _on_disconnect(self, _e) -> None:
        ok, error = self.controller.disconnect()
        if not ok:
            show_snackbar(self.app_page, error or "Falha ao desconectar.", success=False)
            return
        self._last_qr_src = ""
        self.selected_conversation_id = None
        self.messages_column.controls.clear()
        self._set_compose_enabled(False)
        show_snackbar(self.app_page, "Sessão WhatsApp encerrada.", success=True)
        self._render_page()
