"""Controller do módulo WhatsApp com ponte local Node.js."""

from __future__ import annotations

from dataclasses import dataclass

import requests

from controllers.whatsapp_bridge_client import (
    NODE_DOWNLOAD_URL,
    WhatsAppBridgeClient,
    WhatsAppBridgeProcess,
)
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


@dataclass(frozen=True)
class WhatsAppMessage:
    """Mensagem exibida no histórico do chat."""

    from_me: bool
    text: str
    time: str
    timestamp: int = 0
    msg_type: str = "text"


class WhatsAppController:
    """Orquestra ponte Baileys, sessão persistente e mensagens."""

    def __init__(self) -> None:
        self.client = WhatsAppBridgeClient()
        self.bridge_error = ""
        self.last_qr = ""

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
        return str(payload.get("phone") or "")

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
            conversations.append(
                WhatsAppConversation(
                    id=str(row.get("id") or ""),
                    name=str(row.get("name") or "Contato"),
                    phone=str(row.get("phone") or ""),
                    last_message=str(row.get("last_message") or ""),
                    unread=int(row.get("unread") or 0),
                )
            )
        return conversations

    def get_messages(self, conversation_id: str) -> list[WhatsAppMessage]:
        if not conversation_id:
            return []
        try:
            rows = self.client.list_messages(conversation_id)
        except requests.RequestException:
            return []
        messages: list[WhatsAppMessage] = []
        for row in rows:
            messages.append(
                WhatsAppMessage(
                    from_me=bool(row.get("from_me")),
                    text=str(row.get("text") or ""),
                    time=str(row.get("time") or ""),
                    timestamp=int(row.get("timestamp") or 0),
                    msg_type=str(row.get("type") or "text"),
                )
            )
        messages.sort(key=lambda item: item.timestamp)
        return messages

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
