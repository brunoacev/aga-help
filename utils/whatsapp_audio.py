"""Reprodução de áudios do WhatsApp baixados pela ponte local."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

import requests

_PROCESS: subprocess.Popen | None = None


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


def _play_with_ffplay(path: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            os.unlink(path)
        except OSError:
            pass
        if proc.returncode == 0:
            return True, ""
    except FileNotFoundError:
        pass
    except Exception as exc:
        return False, f"Erro ao reproduzir com ffplay: {exc}"
    return False, ""


def _play_with_powershell(path: str) -> tuple[bool, str]:
    if sys.platform != "win32":
        return False, ""
    file_uri = "file:///" + path.replace("\\", "/")
    script = f"""
Add-Type -AssemblyName presentationCore
$p = New-Object System.Windows.Media.MediaPlayer
$p.Open([uri]::new('{file_uri}'))
$p.Play()
Start-Sleep -Milliseconds 400
$wait = 0
while ($p.NaturalDuration.HasTimeSpan -eq $false -and $wait -lt 50) {{
  Start-Sleep -Milliseconds 100
  $wait++
}}
if ($p.NaturalDuration.HasTimeSpan) {{
  Start-Sleep -Seconds ([math]::Ceiling($p.NaturalDuration.TimeSpan.TotalSeconds) + 1)
}} else {{
  Start-Sleep -Seconds 8
}}
"""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            os.unlink(path)
        except OSError:
            pass
        if proc.returncode == 0:
            return True, ""
    except Exception as exc:
        return False, f"Erro ao reproduzir áudio: {exc}"
    return False, ""


def _play_with_system(path: str) -> tuple[bool, str]:
    global _PROCESS
    try:
        if _PROCESS and _PROCESS.poll() is None:
            _PROCESS.terminate()
    except Exception:
        pass
    try:
        if sys.platform == "win32":
            _PROCESS = subprocess.Popen(["cmd", "/c", "start", "", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, ""
        if sys.platform == "darwin":
            _PROCESS = subprocess.Popen(["open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, ""
        _PROCESS = subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

    for player in (_play_with_ffplay, _play_with_powershell, _play_with_system):
        ok, error = player(path)
        if ok:
            return True, ""

    try:
        os.unlink(path)
    except OSError:
        pass
    return False, error or "Não foi possível reproduzir o áudio."
