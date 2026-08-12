"""Testes da view WhatsApp."""

from controllers.whatsapp_controller import WhatsAppController
from utils.qr_code import generate_qr_base64


def test_whatsapp_controller_mock_conversations():
    controller = WhatsAppController()
    conversations = controller.list_conversations()
    assert len(conversations) >= 2
    assert conversations[0].phone.startswith("+55")


def test_whatsapp_controller_messages_by_conversation():
    controller = WhatsAppController()
    messages = controller.get_messages("1")
    assert messages
    assert any(not message.from_me for message in messages)


def test_generate_qr_for_session_token():
    controller = WhatsAppController()
    qr_base64 = generate_qr_base64(controller.session_token)
    assert qr_base64
