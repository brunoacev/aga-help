"""Controller do módulo WhatsApp com ponte local Node.js."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import requests

from controllers.whatsapp_bridge_client import (
    NODE_DOWNLOAD_URL,
    WhatsAppBridgeClient,
    WhatsAppBridgeProcess,
)
from core.db.contacts_repository import find_contact_by_phone
from utils.formatting import format_br_phone
from utils.qr_code import qr_data_uri

STATUS_DISCONNECTED = "DISCONNECTED"
STATUS_QR_READY = "QR_READY"
STATUS_CONNECTED = "CONNECTED"


@dataclass(frozen=True)
class WhatsAppConversation:
    """Conversa exibida no painel esquerdo."""

    id: str
    name: str
    phone: str
    last_message: str
    unread: int = 0
    is_group: bool = False
    group_name: str = ""
    avatar: str = ""
    contact_name: str = ""
    last_message_time: str = ""
    timestamp: int = 0


@dataclass(frozen=True)
class WhatsAppMessage:
    """Mensagem exibida no histórico do chat."""

    from_me: bool
    text: str
    time: str
    timestamp: int = 0
    msg_type: str = "text"
    sender_name: str = ""
    sender_phone: str = ""
    sender_jid: str = ""
    message_id: str = ""
    has_media: bool = False


class WhatsAppController:
    """Orquestra ponte Baileys, sessão persistente e mensagens."""

    def __init__(self) -> None:
        self.client = WhatsAppBridgeClient()
        self.bridge_error = ""
        self.last_qr = ""
        self.active_chat_id: str | None = None
        self._conversations_cache: list[WhatsAppConversation] = []

    @property
    def node_available(self) -> bool:
        return WhatsAppBridgeProcess.is_node_installed()

    @property
    def node_download_url(self) -> str:
        return NODE_DOWNLOAD_URL

    @property
    def connected(self) -> bool:
        return self.get_connection_status() == STATUS_CONNECTED

    @property
    def connected_phone(self) -> str:
        payload = self._safe_status()
        return format_br_phone(str(payload.get("phone") or ""))

    def ensure_bridge_started(self) -> tuple[bool, str]:
        if not self.node_available:
            self.bridge_error = "Node.js não está instalado."
            return False, self.bridge_error
        started, error = WhatsAppBridgeProcess.start()
        self.bridge_error = error
        return started, error

    def get_connection_status(self) -> str:
        payload = self._safe_status()
        status = str(payload.get("status") or STATUS_DISCONNECTED).upper()
        if status not in {STATUS_DISCONNECTED, STATUS_QR_READY, STATUS_CONNECTED}:
            return STATUS_DISCONNECTED
        return status

    def fetch_qr_string(self) -> str:
        try:
            qr = self.client.get_qr()
            if qr:
                self.last_qr = qr
            return qr or self.last_qr
        except requests.RequestException:
            return self.last_qr

    def fetch_qr_image_src(self) -> str:
        qr = self.fetch_qr_string()
        if not qr:
            return ""
        return qr_data_uri(qr)

    def list_conversations(self) -> list[WhatsAppConversation]:
        try:
            rows = self.client.list_chats()
        except requests.RequestException:
            return []
        conversations: list[WhatsAppConversation] = []
        for row in rows:
            is_group = bool(row.get("is_group")) or str(row.get("id") or "").endswith("@g.us")
            chat_id = str(row.get("id") or "")
            raw_phone = str(row.get("phone") or "")
            if not is_group and not raw_phone and chat_id and not chat_id.endswith("@lid"):
                raw_phone = chat_id
            formatted_phone = "" if is_group else format_br_phone(raw_phone)
            group_name = str(row.get("group_name") or row.get("name") or "Grupo")
            contact_name = str(row.get("contact_name") or row.get("name") or "").strip()
            if not is_group and contact_name and (
                "@" in contact_name
                or (formatted_phone and format_br_phone(contact_name) == formatted_phone)
            ):
                contact_name = ""
            if not is_group and not contact_name and formatted_phone:
                local = find_contact_by_phone(formatted_phone)
                if local and local.get("name"):
                    contact_name = str(local["name"]).strip()
            timestamp = int(row.get("timestamp") or 0)
            conversations.append(
                WhatsAppConversation(
                    id=chat_id,
                    name=group_name if is_group else (contact_name or formatted_phone or "Contato"),
                    phone=formatted_phone,
                    last_message=str(row.get("last_message") or ""),
                    unread=int(row.get("unread") or 0),
                    is_group=is_group,
                    group_name=group_name if is_group else "",
                    avatar=str(row.get("avatar") or ""),
                    contact_name="" if is_group else contact_name,
                    last_message_time=format_chat_timestamp(timestamp),
                    timestamp=timestamp,
                )
            )
        self._conversations_cache = conversations
        return conversations

    def get_cached_conversations(self) -> list[WhatsAppConversation]:
        return list(self._conversations_cache)

    def set_active_chat(self, conversation_id: str) -> WhatsAppConversation | None:
        clean_id = (conversation_id or "").strip()
        self.active_chat_id = clean_id or None
        return self.get_active_conversation()

    def get_active_conversation(self) -> WhatsAppConversation | None:
        if not self.active_chat_id:
            return None
        for conversation in self._conversations_cache:
            if conversation.id == self.active_chat_id:
                return conversation
        refreshed = self.list_conversations()
        for conversation in refreshed:
            if conversation.id == self.active_chat_id:
                return conversation
        return None

    def clear_active_chat(self) -> None:
        self.active_chat_id = None

    def build_order_prefill(self, conversation: WhatsAppConversation | None) -> dict | None:
        """Monta dados para o formulário de pedido a partir de uma conversa individual."""
        if not conversation or conversation.is_group:
            return None

        phone = (conversation.phone or "").strip()
        if not phone and conversation.id and not conversation.id.endswith("@lid"):
            phone = format_br_phone(conversation.id)
        if not phone:
            return None

        reseller_name = (conversation.contact_name or "").strip()
        address = ""
        local = find_contact_by_phone(phone)
        if local:
            if not reseller_name:
                reseller_name = str(local.get("name") or "").strip()
            address = str(local.get("address") or "").strip()

        if not reseller_name:
            fallback = (conversation.name or "").strip()
            if fallback and format_br_phone(fallback) != phone:
                reseller_name = fallback

        return {
            "phone": phone,
            "reseller_name": reseller_name,
            "address": address,
        }

    def filter_conversations(self, query: str) -> list[WhatsAppConversation]:
        conversations = self._conversations_cache or self.list_conversations()
        needle = (query or "").strip().lower()
        if not needle:
            return conversations
        filtered: list[WhatsAppConversation] = []
        for item in conversations:
            haystack = (
                item.name.lower(),
                (item.contact_name or "").lower(),
                item.phone.lower(),
                (item.group_name or "").lower(),
                format_br_phone(item.phone).lower(),
                item.last_message.lower(),
                item.id.lower(),
            )
            if any(needle in value for value in haystack if value):
                filtered.append(item)
            elif item.is_group and needle in "grupo":
                filtered.append(item)
        return filtered

    def get_messages(self, conversation_id: str) -> list[WhatsAppMessage]:
        if not conversation_id:
            return []
        try:
            rows = self.client.list_messages(conversation_id)
        except requests.RequestException:
            return []
        messages: list[WhatsAppMessage] = []
        for row in rows:
            sender_phone_raw = str(row.get("sender_phone") or "")
            messages.append(
                WhatsAppMessage(
                    from_me=bool(row.get("from_me")),
                    text=str(row.get("text") or ""),
                    time=str(row.get("time") or ""),
                    timestamp=int(row.get("timestamp") or 0),
                    msg_type=str(row.get("type") or "text"),
                    sender_name=str(row.get("sender_name") or ""),
                    sender_phone=format_br_phone(sender_phone_raw) if sender_phone_raw else "",
                    sender_jid=str(row.get("sender_jid") or ""),
                    message_id=str(row.get("id") or ""),
                    has_media=bool(row.get("has_media")) or str(row.get("type") or "") == "audio",
                )
            )
        messages.sort(key=lambda item: item.timestamp)
        return messages

    def get_media_url(self, conversation_id: str, message_id: str) -> str:
        return self.client.get_media_url(conversation_id, message_id)

    def mark_conversation_read(self, conversation_id: str) -> None:
        if not conversation_id:
            return
        try:
            self.client.mark_read(conversation_id)
        except requests.RequestException:
            pass

    def send_message(self, conversation_id: str, message: str) -> tuple[bool, str]:
        clean = (message or "").strip()
        if not clean:
            return False, "Digite uma mensagem."
        if not conversation_id:
            return False, "Selecione uma conversa."
        try:
            payload = self.client.send_message(conversation_id, clean)
            if payload.get("ok"):
                return True, ""
            return False, str(payload.get("error") or "Falha ao enviar.")
        except requests.RequestException as exc:
            return False, f"Erro de comunicação com a ponte: {exc}"

    @staticmethod
    def build_outgoing_message(text: str) -> WhatsAppMessage:
        """Monta mensagem otimista para exibição imediata na UI."""
        from datetime import datetime

        now = datetime.now()
        return WhatsAppMessage(
            from_me=True,
            text=text.strip(),
            time=now.strftime("%H:%M"),
            timestamp=int(now.timestamp() * 1000),
            msg_type="text",
        )

    def disconnect(self) -> tuple[bool, str]:
        try:
            payload = self.client.logout()
            self.last_qr = ""
            if payload.get("ok"):
                return True, ""
            return False, str(payload.get("error") or "Falha ao desconectar.")
        except requests.RequestException as exc:
            return False, str(exc)

    def regenerate_qr(self) -> tuple[bool, str]:
        try:
            payload = self.client.restart()
            self.last_qr = ""
            if payload.get("ok"):
                return True, ""
            return False, str(payload.get("error") or "Falha ao gerar novo QR Code.")
        except requests.RequestException as exc:
            return False, str(exc)

    def _safe_status(self) -> dict:
        try:
            return self.client.get_status()
        except requests.RequestException:
            return {"status": STATUS_DISCONNECTED, "phone": ""}


def format_chat_timestamp(timestamp: int) -> str:
    """Formata timestamp da conversa para exibição compacta na lista."""
    if not timestamp:
        return ""
    ts = timestamp
    if ts > 1_000_000_000_000:
        ts //= 1000
    try:
        dt = datetime.fromtimestamp(ts)
    except (OSError, OverflowError, ValueError):
        return ""
    now = datetime.now()
    if dt.date() == now.date():
        return dt.strftime("%H:%M")
    if dt.year == now.year:
        return dt.strftime("%d/%m")
    return dt.strftime("%d/%m/%y")
