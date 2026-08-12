"""Controller mockado do módulo WhatsApp (base para integração futura)."""

from __future__ import annotations

import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class WhatsAppConversation:
    """Conversa ativa exibida no painel esquerdo."""

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


MOCK_CONVERSATIONS: tuple[WhatsAppConversation, ...] = (
    WhatsAppConversation("1", "Revenda Solar", "+55 11 98765-4321", "Pedido #1042 pronto?", 2),
    WhatsAppConversation("2", "Casa & Design", "+55 21 99887-6655", "Obrigado pelo orçamento!", 0),
    WhatsAppConversation("3", "Persianas Premium", "+55 31 97654-3210", "Pode confirmar a medida?", 1),
)

MOCK_MESSAGES: dict[str, tuple[WhatsAppMessage, ...]] = {
    "1": (
        WhatsAppMessage(False, "Olá! Como está o pedido #1042?", "09:12"),
        WhatsAppMessage(True, "Bom dia! Está em produção, previsão para amanhã.", "09:18"),
        WhatsAppMessage(False, "Pedido #1042 pronto?", "14:05"),
    ),
    "2": (
        WhatsAppMessage(True, "Segue o orçamento atualizado em anexo.", "11:40"),
        WhatsAppMessage(False, "Obrigado pelo orçamento!", "11:52"),
    ),
    "3": (
        WhatsAppMessage(False, "Boa tarde, pode confirmar a medida da janela?", "16:20"),
        WhatsAppMessage(True, "Claro! Qual ambiente você mediu?", "16:25"),
        WhatsAppMessage(False, "Pode confirmar a medida?", "16:31"),
    ),
}


class WhatsAppController:
    """Estado simulado de sessão e conversas."""

    def __init__(self) -> None:
        self.connected = False
        self.connected_phone = "+55 11 98765-4321"
        self.session_token = self.new_session_token()

    @staticmethod
    def new_session_token() -> str:
        return f"aga-help-whatsapp-{secrets.token_urlsafe(16)}"

    def list_conversations(self) -> list[WhatsAppConversation]:
        return list(MOCK_CONVERSATIONS)

    def get_messages(self, conversation_id: str) -> list[WhatsAppMessage]:
        return list(MOCK_MESSAGES.get(conversation_id, ()))

    def connect(self, phone: str | None = None) -> None:
        self.connected = True
        if phone:
            self.connected_phone = phone

    def disconnect(self) -> None:
        self.connected = False
        self.session_token = self.new_session_token()

    def refresh_session_token(self) -> str:
        self.session_token = self.new_session_token()
        self.connected = False
        return self.session_token
