"""Cliente HTTP da ponte local WhatsApp (Node.js + Baileys)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from urllib.parse import quote

import requests

BRIDGE_PORT = int(os.getenv("WHATSAPP_BRIDGE_PORT", "5001"))
BRIDGE_BASE_URL = f"http://127.0.0.1:{BRIDGE_PORT}"
BRIDGE_DIR = Path(__file__).resolve().parent.parent / "whatsapp_bridge"
BRIDGE_ENTRY = BRIDGE_DIR / "index.js"
NODE_DOWNLOAD_URL = "https://nodejs.org/"
REQUEST_TIMEOUT = 8


class WhatsAppBridgeProcess:
    """Gerencia o subprocesso Node.js da ponte WhatsApp."""

    _process: subprocess.Popen | None = None

    @classmethod
    def is_node_installed(cls) -> bool:
        return shutil.which("node") is not None

    @classmethod
    def is_running(cls) -> bool:
        return cls._process is not None and cls._process.poll() is None

    @classmethod
    def ensure_dependencies(cls) -> tuple[bool, str]:
        if not cls.is_node_installed():
            return False, "Node.js não encontrado."
        node_modules = BRIDGE_DIR / "node_modules"
        if node_modules.exists():
            return True, ""
        npm = shutil.which("npm")
        if not npm:
            return False, "npm não encontrado. Instale o Node.js completo."
        result = subprocess.run(
            [npm, "install"],
            cwd=str(BRIDGE_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            return False, detail or "Falha ao executar npm install."
        return True, ""

    @classmethod
    def start(cls) -> tuple[bool, str]:
        ok, error = cls.ensure_dependencies()
        if not ok:
            return False, error
        if cls.is_running():
            return True, ""
        if not BRIDGE_ENTRY.exists():
            return False, "Arquivo whatsapp_bridge/index.js não encontrado."

        kwargs: dict = {
            "cwd": str(BRIDGE_DIR),
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if sys.platform == "win32" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        cls._process = subprocess.Popen(["node", str(BRIDGE_ENTRY)], **kwargs)
        if not cls.wait_until_ready(timeout=35):
            return False, "Ponte WhatsApp não respondeu a tempo."
        return True, ""

    @classmethod
    def wait_until_ready(cls, timeout: float = 30.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if cls._process and cls._process.poll() is not None:
                return False
            try:
                response = requests.get(f"{BRIDGE_BASE_URL}/health", timeout=1.5)
                if response.ok:
                    return True
            except requests.RequestException:
                pass
            time.sleep(0.4)
        return False

    @classmethod
    def stop(cls) -> None:
        if cls._process and cls._process.poll() is None:
            cls._process.terminate()
            try:
                cls._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls._process.kill()
        cls._process = None


class WhatsAppBridgeClient:
    """Chamadas HTTP para a ponte local."""

    def __init__(self, base_url: str = BRIDGE_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, **params) -> dict:
        response = requests.get(
            f"{self.base_url}{path}",
            params=params or None,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    def _post(self, path: str, payload: dict | None = None) -> dict:
        response = requests.post(
            f"{self.base_url}{path}",
            json=payload or {},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else {}

    def get_status(self) -> dict:
        return self._get("/status")

    def get_qr(self) -> str:
        payload = self._get("/qr")
        return str(payload.get("qr") or "")

    def list_chats(self) -> list[dict]:
        payload = self._get("/chats")
        chats = payload.get("chats") or []
        return chats if isinstance(chats, list) else []

    def list_messages(self, chat_id: str) -> list[dict]:
        payload = self._get("/messages", chat_id=chat_id)
        messages = payload.get("messages") or []
        return messages if isinstance(messages, list) else []

    def get_media_url(self, chat_id: str, message_id: str) -> str:
        return (
            f"{self.base_url}/media"
            f"?chat_id={quote(chat_id, safe='@.:')}"
            f"&msg_id={quote(message_id, safe='')}"
        )

    def send_message(self, chat_id: str, message: str) -> dict:
        return self._post("/send", {"chat_id": chat_id, "message": message})

    def mark_read(self, chat_id: str) -> dict:
        return self._post("/read", {"chat_id": chat_id})

    def logout(self) -> dict:
        return self._post("/logout")

    def restart(self) -> dict:
        return self._post("/restart")
