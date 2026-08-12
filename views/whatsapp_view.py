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
    WhatsAppMessage,
)
from core import colors
from utils.formatting import format_br_phone
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric, show_snackbar
from utils.ui_theme import FONT_BODY, FONT_CAPTION, RADIUS, S1, S2, S3, S4, field_style, page_header, text_section_heading
from utils.whatsapp_audio import play_audio_from_url

QR_INSTRUCTIONS = "Abra o WhatsApp > Aparelhos conectados > Conectar um aparelho"
NODE_DOWNLOAD_URL = "https://nodejs.org/"
LEFT_PANEL_WIDTH = 360
POLL_INTERVAL_SECONDS = 2


class WhatsAppView(ft.Container):
    """Painel de conversas e chat estilo WhatsApp Web."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        self.controller = WhatsAppController()
        self.border_all = border_all(colors.BORDER_COLOR)
        self.selected_conversation_id: str | None = None
        self._polling = False
        self._last_status = STATUS_DISCONNECTED
        self._last_qr_src = ""
        self._sync_index: dict[str, int] = {}
        self._pending_optimistic: dict[str, str] = {}
        self._selected_is_group = False
        self._chat_filter = ""
        self._group_icon = getattr(ft.Icons, "GROUPS", None) or getattr(ft.Icons, "SUPERGROUP", None) or "groups"

        self.node_alert = ft.Container(
            visible=False,
            bgcolor=colors.WA_PANEL_BG,
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
                        color=colors.WA_LIST_PREVIEW,
                    ),
                    ft.TextButton(content="Baixar Node.js", url=NODE_DOWNLOAD_URL),
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
            color=colors.WA_LIST_PREVIEW,
            weight=ft.FontWeight.W_600,
        )
        self.qr_panel = ft.Column(
            [
                ft.Container(content=self.qr_image, alignment=get_alignment_center()),
                ft.Text(
                    QR_INSTRUCTIONS,
                    size=FONT_CAPTION,
                    color=colors.WA_LIST_PREVIEW,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Button(
                    content="Gerar Novo QrCode",
                    icon=getattr(ft.Icons, "QR_CODE_SCANNER", None) or "qr_code_scanner",
                    bgcolor=colors.WA_ACCENT,
                    color=colors.WA_BUBBLE_TEXT,
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
                    ft.Icon(getattr(ft.Icons, "VERIFIED", None) or "verified", color=colors.WA_ACCENT, size=18),
                    ft.Text("", size=FONT_BODY, color=colors.WA_BUBBLE_TEXT, weight=ft.FontWeight.W_600),
                ],
                spacing=S2,
            ),
            bgcolor=colors.WA_INCOMING_BUBBLE,
            border=border_all(colors.WA_ACCENT),
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

        self.txt_search = ft.TextField(
            hint_text="Buscar conversa...",
            prefix_icon=getattr(ft.Icons, "SEARCH", None) or "search",
            on_change=self._on_search_conversations,
            **field_style(),
        )
        self.conversations_column = ft.Column(
            spacing=S1,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        self.chat_header_icon = ft.Icon(self._group_icon, size=20, color=colors.WA_ACCENT, visible=False)
        self.chat_header_text = ft.Text(
            "Selecione uma conversa",
            size=FONT_BODY,
            color=colors.WA_LIST_NAME,
            weight=ft.FontWeight.W_600,
            expand=True,
        )
        self.chat_header = ft.Row(
            [self.chat_header_icon, self.chat_header_text],
            spacing=S2,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.messages_list = ft.ListView(
            expand=True,
            spacing=S2,
            padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            auto_scroll=True,
        )
        self.chat_empty_hint = ft.Text(
            "Selecione uma conversa para ver as mensagens.",
            size=FONT_CAPTION,
            color=colors.WA_LIST_PREVIEW,
            visible=True,
        )
        self.txt_message = ft.TextField(
            hint_text="Digite uma mensagem (Enter para enviar)",
            expand=True,
            multiline=False,
            disabled=True,
            on_submit=self._on_send_message,
            **field_style(),
        )
        self.btn_send = ft.IconButton(
            icon=getattr(ft.Icons, "SEND_ROUNDED", None) or "send",
            icon_color=colors.WA_BUBBLE_TEXT,
            bgcolor=colors.WA_ACCENT,
            tooltip="Enviar",
            disabled=True,
            on_click=self._on_send_message,
        )
        self.compose_row = ft.Container(
            bgcolor=colors.WA_PANEL_BG,
            border_radius=RADIUS,
            padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=getattr(ft.Icons, "ATTACH_FILE", None) or "attach_file",
                        icon_color=colors.WA_LIST_PREVIEW,
                        tooltip="Anexo (em breve)",
                        disabled=True,
                    ),
                    self.txt_message,
                    self.btn_send,
                ],
                spacing=S2,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
        )

        left_panel = ft.Container(
            width=LEFT_PANEL_WIDTH,
            bgcolor=colors.WA_PANEL_BG,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S3,
            content=ft.Column(
                [
                    text_section_heading("Status da Conexão"),
                    self.node_alert,
                    self.lbl_connection_status,
                    self.qr_panel,
                    self.connected_panel,
                    ft.Divider(height=1, color=colors.BORDER_COLOR),
                    text_section_heading("Conversas"),
                    self.txt_search,
                    ft.Container(content=self.conversations_column, expand=True),
                ],
                spacing=S3,
                expand=True,
            ),
        )

        chat_panel = ft.Container(
            expand=True,
            bgcolor=colors.WA_CHAT_BG,
            border=self.border_all,
            border_radius=RADIUS,
            padding=make_padding_symmetric(horizontal=S3, vertical=S3),
            content=ft.Column(
                [
                    ft.Container(
                        bgcolor=colors.WA_PANEL_BG,
                        border_radius=RADIUS,
                        padding=make_padding_symmetric(horizontal=S3, vertical=S2),
                        content=self.chat_header,
                    ),
                    ft.Container(content=self.messages_list, expand=True),
                    self.chat_empty_hint,
                    self.compose_row,
                ],
                spacing=S2,
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
                        "Chat em tempo real — mensagens novas aparecem sempre por último.",
                    ),
                    ft.Row(
                        [left_panel, chat_panel],
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
                self.lbl_connected_badge.content.controls[1].value = f"Conectado como {format_br_phone(phone) or phone}"
                self.qr_panel.visible = False
                self.connected_panel.visible = True
                self.qr_image.visible = False
                self._set_status_label("Conectado", colors.WA_ACCENT)
                self._set_compose_enabled(bool(self.selected_conversation_id))
                self._render_conversation_list()
                if self.selected_conversation_id:
                    self._sync_new_messages(self.selected_conversation_id, scroll_to_bottom=True, update=False)
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
        if not self.app_page or not self._polling:
            return
        try:
            self.app_page.update()
        except RuntimeError:
            self._polling = False

    async def _scroll_chat_to_bottom(self, duration: int = 300) -> None:
        if not self.messages_list.controls:
            return
        for kwargs in ({"offset": -1, "duration": duration}, {"scroll_key": -1, "duration": duration}):
            try:
                result = self.messages_list.scroll_to(**kwargs)
                if asyncio.iscoroutine(result):
                    await result
                return
            except (TypeError, ValueError, AttributeError, RuntimeError):
                continue

    def _schedule_scroll_to_bottom(self, *, duration: int = 300) -> None:
        if self.app_page and self._polling:
            self.app_page.run_task(self._scroll_chat_to_bottom, duration)

    def _on_search_conversations(self, e) -> None:
        self._chat_filter = (e.control.value or "").strip().lower()
        self._render_conversation_list()
        self._render_page()

    def _filtered_conversations(self) -> list[WhatsAppConversation]:
        conversations = self.controller.list_conversations()
        if not self._chat_filter:
            return conversations
        return [
            item
            for item in conversations
            if self._chat_filter in item.name.lower()
            or self._chat_filter in (item.contact_name or "").lower()
            or self._chat_filter in item.phone.lower()
            or self._chat_filter in (item.group_name or "").lower()
            or self._chat_filter in format_br_phone(item.phone).lower()
            or self._chat_filter in item.last_message.lower()
            or (item.is_group and self._chat_filter in "grupo")
        ]

    def _render_conversation_list(self) -> None:
        conversations = self._filtered_conversations()
        self.conversations_column.controls.clear()
        if not conversations:
            self.conversations_column.controls.append(
                ft.Text(
                    "Nenhuma conversa encontrada.",
                    size=FONT_CAPTION,
                    color=colors.WA_LIST_PREVIEW,
                )
            )
            return
        for conversation in conversations:
            self.conversations_column.controls.append(self._build_conversation_tile(conversation))

    def _load_conversations(self) -> None:
        conversations = self._filtered_conversations()
        self._render_conversation_list()
        if not conversations:
            self.selected_conversation_id = None
            self.chat_empty_hint.visible = True
            self._set_compose_enabled(False)
            return
        valid_ids = {item.id for item in conversations}
        if self.selected_conversation_id not in valid_ids:
            self._select_conversation(conversations[0].id, update=False)

    def _conversation_contact_name(self, conversation: WhatsAppConversation) -> str:
        if conversation.is_group:
            return conversation.group_name or conversation.name or "Grupo"
        return (conversation.contact_name or "").strip()

    def _conversation_phone_line(self, conversation: WhatsAppConversation) -> str:
        if conversation.is_group:
            return ""
        if conversation.phone:
            return format_br_phone(conversation.phone) or conversation.phone
        if conversation.id.endswith("@lid"):
            return ""
        return format_br_phone(conversation.id)

    def _build_conversation_tile(self, conversation: WhatsAppConversation) -> ft.Container:
        is_active = conversation.id == self.selected_conversation_id
        preview_color = colors.WA_LIST_NAME if conversation.unread else colors.WA_LIST_PREVIEW
        preview = conversation.last_message or "Sem mensagens"
        contact_name = self._conversation_contact_name(conversation)
        phone_line = self._conversation_phone_line(conversation)

        text_lines: list[ft.Control] = []
        if conversation.is_group:
            text_lines.append(
                ft.Text(
                    contact_name,
                    size=FONT_BODY,
                    weight=ft.FontWeight.W_600,
                    color=colors.WA_LIST_NAME,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True,
                )
            )
        else:
            if contact_name:
                text_lines.append(
                    ft.Text(
                        contact_name,
                        size=FONT_BODY,
                        weight=ft.FontWeight.W_600,
                        color=colors.WA_LIST_NAME,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    )
                )
            if phone_line:
                text_lines.append(
                    ft.Text(
                        phone_line,
                        size=10,
                        color=colors.WA_META_INCOMING,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    )
                )
        text_lines.append(
            ft.Text(
                preview,
                size=FONT_CAPTION,
                color=preview_color,
                overflow=ft.TextOverflow.ELLIPSIS,
                expand=True,
            )
        )

        tile = ft.Container(
            content=ft.Column(
                text_lines,
                spacing=S1,
            ),
            padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            border_radius=RADIUS,
            bgcolor=colors.WA_LIST_ACTIVE if is_active else colors.WA_PANEL_BG,
        )

        def on_hover(e, container=tile, active=is_active):
            container.bgcolor = (
                colors.WA_LIST_ACTIVE
                if active
                else (colors.WA_INCOMING_BUBBLE if e.data == "true" else colors.WA_PANEL_BG)
            )
            try:
                container.update()
            except RuntimeError:
                pass

        return ft.GestureDetector(
            content=tile,
            mouse_cursor=ft.MouseCursor.CLICK,
            on_tap=lambda _e, cid=conversation.id: self._select_conversation(cid),
            on_hover=on_hover,
            expand=True,
        )

    def _sender_label(self, message: WhatsAppMessage) -> str:
        if message.sender_name:
            return message.sender_name
        if message.sender_phone:
            return format_br_phone(message.sender_phone) or message.sender_phone
        if message.sender_jid:
            return format_br_phone(message.sender_jid) or message.sender_jid
        return ""

    def _build_message_bubble(self, message: WhatsAppMessage) -> ft.Control:
        outgoing = message.from_me
        bubble_bg = colors.WA_OUTGOING_BUBBLE if outgoing else colors.WA_INCOMING_BUBBLE
        meta_color = colors.WA_META_OUTGOING if outgoing else colors.WA_META_INCOMING
        alignment = ft.MainAxisAlignment.END if outgoing else ft.MainAxisAlignment.START
        status_icon = (
            ft.Icon(
                getattr(ft.Icons, "DONE_ALL", None) or "done_all",
                size=14,
                color=colors.WA_META_OUTGOING,
            )
            if outgoing
            else None
        )
        footer_controls = [
            ft.Text(message.time, size=10, color=meta_color),
        ]
        if status_icon:
            footer_controls.append(status_icon)

        bubble_lines: list[ft.Control] = []
        if self._selected_is_group and not outgoing:
            sender_label = self._sender_label(message)
            if sender_label:
                bubble_lines.append(
                    ft.Text(
                        sender_label,
                        size=10,
                        color=colors.WA_ACCENT,
                        weight=ft.FontWeight.W_600,
                    )
                )
        bubble_lines.extend(
            [
                *self._build_message_body(message),
                ft.Row(footer_controls, spacing=S1, alignment=ft.MainAxisAlignment.END),
            ]
        )

        return ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        bubble_lines,
                        spacing=S1,
                        tight=True,
                    ),
                    bgcolor=bubble_bg,
                    border_radius=RADIUS,
                    padding=make_padding_symmetric(horizontal=S3, vertical=S2),
                    width=360,
                ),
            ],
            alignment=alignment,
        )

    def _build_message_body(self, message: WhatsAppMessage) -> list[ft.Control]:
        if message.msg_type == "audio" and message.message_id and self.selected_conversation_id:
            play_icon = getattr(ft.Icons, "PLAY_ARROW", None) or getattr(ft.Icons, "PLAY_CIRCLE", None) or "play_arrow"
            return [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=play_icon,
                            icon_color=colors.WA_BUBBLE_TEXT,
                            bgcolor=colors.WA_ACCENT,
                            tooltip="Reproduzir áudio",
                            on_click=lambda _e, mid=message.message_id: self._on_play_audio(mid),
                        ),
                        ft.Text(
                            "Mensagem de voz",
                            size=FONT_BODY,
                            color=colors.WA_BUBBLE_TEXT,
                        ),
                    ],
                    spacing=S2,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ]
        return [
            ft.Text(
                message.text,
                size=FONT_BODY,
                color=colors.WA_BUBBLE_TEXT,
                selectable=True,
            )
        ]

    def _on_play_audio(self, message_id: str) -> None:
        if not self.selected_conversation_id or not message_id:
            show_snackbar(self.app_page, "Áudio indisponível.", success=False)
            return
        if self.app_page:
            self.app_page.run_task(self._play_audio_async, self.selected_conversation_id, message_id)

    async def _play_audio_async(self, chat_id: str, message_id: str) -> None:
        url = self.controller.get_media_url(chat_id, message_id)
        ok, error = await asyncio.to_thread(play_audio_from_url, url)
        if not ok:
            show_snackbar(self.app_page, error or "Não foi possível reproduzir.", success=False)

    def _append_message_bubble(self, message: WhatsAppMessage, *, scroll: bool = True) -> None:
        self.messages_list.controls.append(self._build_message_bubble(message))
        self.chat_empty_hint.visible = False
        if scroll:
            self._schedule_scroll_to_bottom()

    def _reset_chat_messages(self, conversation_id: str) -> None:
        self._sync_index[conversation_id] = 0
        self._pending_optimistic.pop(conversation_id, None)
        self.messages_list.controls.clear()
        messages = self.controller.get_messages(conversation_id)
        for message in messages:
            self._append_message_bubble(message, scroll=False)
        self._sync_index[conversation_id] = len(messages)
        self.chat_empty_hint.visible = not messages
        self._schedule_scroll_to_bottom()

    def _sync_new_messages(
        self,
        conversation_id: str,
        *,
        scroll_to_bottom: bool = False,
        update: bool = True,
    ) -> bool:
        messages = self.controller.get_messages(conversation_id)
        synced = self._sync_index.get(conversation_id, 0)
        pending_text = self._pending_optimistic.get(conversation_id)

        if pending_text and messages and messages[-1].from_me and messages[-1].text == pending_text:
            if self.messages_list.controls and synced < len(messages):
                self.messages_list.controls.pop()
            self._pending_optimistic.pop(conversation_id, None)
            synced = min(synced, len(messages) - 1)

        appended = False
        for message in messages[synced:]:
            self._append_message_bubble(message, scroll=False)
            appended = True

        self._sync_index[conversation_id] = len(messages)
        self.chat_empty_hint.visible = not self.messages_list.controls

        if appended and scroll_to_bottom:
            self._schedule_scroll_to_bottom()

        if update and appended:
            self._render_page()
        return appended

    def _select_conversation(self, conversation_id: str, *, update: bool = True) -> None:
        self.selected_conversation_id = conversation_id
        conversation = next(
            (item for item in self.controller.list_conversations() if item.id == conversation_id),
            None,
        )
        if not conversation:
            return

        self._selected_is_group = conversation.is_group
        self.chat_header_icon.visible = conversation.is_group
        contact_name = self._conversation_contact_name(conversation)
        if conversation.is_group:
            self.chat_header_text.value = contact_name
        else:
            phone = self._conversation_phone_line(conversation)
            self.chat_header_text.value = f"{contact_name}  ·  {phone}" if phone and phone != contact_name else contact_name
        self.controller.mark_conversation_read(conversation_id)
        self._reset_chat_messages(conversation_id)
        self._set_compose_enabled(self._last_status == STATUS_CONNECTED)
        self._render_conversation_list()
        if update:
            self._render_page()

    def _on_send_message(self, _e) -> None:
        if not self.selected_conversation_id:
            show_snackbar(self.app_page, "Selecione uma conversa.", success=False)
            return
        text = (self.txt_message.value or "").strip()
        if not text:
            show_snackbar(self.app_page, "Digite uma mensagem.", success=False)
            return

        chat_id = self.selected_conversation_id
        optimistic = self.controller.build_outgoing_message(text)
        self.txt_message.value = ""
        self._pending_optimistic[chat_id] = text
        self._append_message_bubble(optimistic, scroll=True)
        self._render_page()

        if self.app_page:
            self.app_page.run_task(self._send_message_async, chat_id, text)

    async def _send_message_async(self, chat_id: str, text: str) -> None:
        ok, error = await asyncio.to_thread(self.controller.send_message, chat_id, text)
        if not ok:
            if self._pending_optimistic.get(chat_id) == text and self.messages_list.controls:
                self.messages_list.controls.pop()
            self._pending_optimistic.pop(chat_id, None)
            show_snackbar(self.app_page, error or "Não foi possível enviar.", success=False)
            self._render_page()
            return

        self._sync_new_messages(chat_id, scroll_to_bottom=True, update=False)
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
        self._sync_index.clear()
        self._pending_optimistic.clear()
        self._selected_is_group = False
        self.selected_conversation_id = None
        self.messages_list.controls.clear()
        self._set_compose_enabled(False)
        show_snackbar(self.app_page, "Sessão WhatsApp encerrada.", success=True)
        self._render_page()
