"""Reprodução de áudios do WhatsApp baixados pela ponte local."""

from __future__ import annotations

import os
import sys
import tempfile
import threading

import requests

_lock = threading.Lock()
_player_ready = False


def _ensure_player() -> bool:
    global _player_ready
    if _player_ready:
        return True
    try:
        import pygame

        pygame.mixer.init()
        _player_ready = True
        return True
    except Exception:
        return False


def _download_audio(url: str, timeout: float) -> tuple[str | None, str]:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    content_type = (response.headers.get("content-type") or "").lower()
    if "mpeg" in content_type or "mp3" in content_type:
        suffix = ".mp3"
    else:
        suffix = ".ogg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(response.content)
        return tmp.name, ""


def _play_with_pygame(path: str) -> tuple[bool, str]:
    try:
        import pygame

        with _lock:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

        def _cleanup() -> None:
            import time

            while pygame.mixer.music.get_busy():
                time.sleep(0.2)
            try:
                os.unlink(path)
            except OSError:
                pass

        threading.Thread(target=_cleanup, daemon=True).start()
        return True, ""
    except Exception as exc:
        return False, f"Erro ao reproduzir áudio: {exc}"


def _play_with_system(path: str) -> tuple[bool, str]:
    try:
        if sys.platform == "win32":
            os.startfile(path)  # noqa: S606
            return True, ""
        if sys.platform == "darwin":
            import subprocess

            subprocess.Popen(["open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, ""
        import subprocess

        subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, ""
    except Exception as exc:
        return False, f"Erro ao abrir áudio no sistema: {exc}"


def play_audio_from_url(url: str, timeout: float = 30.0) -> tuple[bool, str]:
    """Baixa e reproduz áudio OGG/MP3 da ponte WhatsApp."""
    try:
        path, error = _download_audio(url, timeout)
        if error or not path:
            return False, error or "Falha ao baixar áudio."
    except requests.RequestException as exc:
        return False, f"Erro ao baixar áudio: {exc}"

    if _ensure_player():
        return _play_with_pygame(path)

    ok, error = _play_with_system(path)
    if ok:
        return True, ""
    try:
        os.unlink(path)
    except OSError:
        pass
    return False, error or "Reprodutor indisponível."
