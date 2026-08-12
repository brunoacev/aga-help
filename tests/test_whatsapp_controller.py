"""Testes do controller WhatsApp com ponte mockada."""

from unittest.mock import MagicMock, patch

from controllers.whatsapp_controller import (
    STATUS_CONNECTED,
    STATUS_QR_READY,
    WhatsAppController,
)
from utils.qr_code import generate_qr_base64, qr_data_uri


def test_fetch_qr_image_src_uses_real_qr_string():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.get_qr.return_value = "2@abc-session-token"
    src = controller.fetch_qr_image_src()
    assert src.startswith("data:image/png;base64,")


def test_list_conversations_from_bridge():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.list_chats.return_value = [
        {
            "id": "558599999999@s.whatsapp.net",
            "name": "Cliente Teste",
            "phone": "+558599999999",
            "last_message": "Olá",
            "unread": 1,
        }
    ]
    conversations = controller.list_conversations()
    assert len(conversations) == 1
    assert conversations[0].phone.startswith("+55")


def test_get_messages_from_bridge():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.list_messages.return_value = [
        {"from_me": False, "text": "Oi", "time": "10:00"},
        {"from_me": True, "text": "Olá!", "time": "10:01"},
    ]
    messages = controller.get_messages("558599999999@s.whatsapp.net")
    assert len(messages) == 2
    assert messages[0].text == "Oi"


def test_connection_status_mapping():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.get_status.return_value = {"status": STATUS_QR_READY, "phone": ""}
    assert controller.get_connection_status() == STATUS_QR_READY
    controller.client.get_status.return_value = {"status": STATUS_CONNECTED, "phone": "+5585..."}
    assert controller.connected is True


def test_send_message_success():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.send_message.return_value = {"ok": True}
    ok, error = controller.send_message("558599999999@s.whatsapp.net", "Teste")
    assert ok
    assert error == ""


@patch("controllers.whatsapp_bridge_client.WhatsAppBridgeProcess.is_node_installed", return_value=True)
@patch("controllers.whatsapp_bridge_client.WhatsAppBridgeProcess.start", return_value=(True, ""))
def test_ensure_bridge_started(_mock_start, _mock_node):
    controller = WhatsAppController()
    ok, error = controller.ensure_bridge_started()
    assert ok
    assert error == ""


def test_qr_data_uri_helper():
    uri = qr_data_uri("session-token")
    assert uri.startswith("data:image/png;base64,")
    assert generate_qr_base64("x")
