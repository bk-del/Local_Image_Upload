from __future__ import annotations

import base64
import io
import re
import socket
from pathlib import Path

import qrcode


def sanitize_stem(value: str) -> str:
    stem = value.strip().lower()
    stem = re.sub(r"\s+", "-", stem)
    stem = re.sub(r"[^a-z0-9._-]", "", stem)
    stem = re.sub(r"-+", "-", stem).strip("-._")
    return stem or "image"


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def detect_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
    except OSError:
        local_ip = "127.0.0.1"
    finally:
        sock.close()
    return local_ip


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def dated_upload_dir(base_dir: Path, folder_name: str) -> Path:
    return ensure_directory(base_dir / folder_name)


def unique_path(directory: Path, desired_stem: str, extension: str) -> Path:
    safe_stem = sanitize_stem(desired_stem)
    candidate = directory / f"{safe_stem}{extension}"
    counter = 1

    while candidate.exists():
        candidate = directory / f"{safe_stem}_{counter}{extension}"
        counter += 1

    return candidate


def make_qr_data_uri(url: str) -> str:
    image = qrcode.make(url)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
