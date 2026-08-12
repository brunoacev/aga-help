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
            "id": "5585999999999@s.whatsapp.net",
            "name": "Maria Silva",
            "contact_name": "Maria Silva",
            "phone": "+5585999999999",
            "last_message": "Olá",
            "unread": 1,
            "is_group": False,
        }
    ]
    conversations = controller.list_conversations()
    assert len(conversations) == 1
    assert conversations[0].contact_name == "Maria Silva"
    assert conversations[0].phone == "+55 (85) 99999-9999"
    assert conversations[0].is_group is False


def test_list_conversations_lid_chat_without_fake_phone():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.list_chats.return_value = [
        {
            "id": "123456789012345@lid",
            "name": "João",
            "contact_name": "João",
            "phone": "+5585988776655",
            "last_message": "Oi",
            "unread": 0,
            "is_group": False,
        }
    ]
    conversations = controller.list_conversations()
    assert conversations[0].contact_name == "João"
    assert conversations[0].phone == "+55 (85) 98877-6655"


def test_list_group_conversations_from_bridge():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.list_chats.return_value = [
        {
            "id": "120363012345678901@g.us",
            "name": "Equipe Agatek",
            "phone": "",
            "group_name": "Equipe Agatek",
            "last_message": "Bom dia",
            "unread": 0,
            "is_group": True,
            "avatar": "https://example.com/group.jpg",
        }
    ]
    conversations = controller.list_conversations()
    assert len(conversations) == 1
    assert conversations[0].is_group is True
    assert conversations[0].group_name == "Equipe Agatek"
    assert conversations[0].name == "Equipe Agatek"
    assert conversations[0].phone == ""


def test_get_group_messages_with_sender():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.list_messages.return_value = [
        {
            "from_me": False,
            "text": "Oi pessoal",
            "time": "10:00",
            "sender_name": "Maria",
            "sender_phone": "+5585999999999",
            "sender_jid": "5585999999999@s.whatsapp.net",
        },
    ]
    messages = controller.get_messages("120363012345678901@g.us")
    assert len(messages) == 1
    assert messages[0].sender_name == "Maria"
    assert messages[0].sender_phone == "+55 (85) 99999-9999"


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


def test_get_audio_messages_from_bridge():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.list_messages.return_value = [
        {
            "id": "ABC123",
            "from_me": False,
            "text": "🎤 Áudio",
            "time": "10:00",
            "type": "audio",
            "has_media": True,
        },
    ]
    messages = controller.get_messages("5585999999999@s.whatsapp.net")
    assert messages[0].msg_type == "audio"
    assert messages[0].has_media is True
    assert messages[0].message_id == "ABC123"


def test_get_media_url():
    controller = WhatsAppController()
    controller.client = MagicMock()
    controller.client.get_media_url.return_value = "http://127.0.0.1:5001/media?chat_id=x&msg_id=y"
    url = controller.get_media_url("5585999999999@s.whatsapp.net", "ABC123")
    assert "media" in url
    controller.client.get_media_url.assert_called_once_with("5585999999999@s.whatsapp.net", "ABC123")


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
