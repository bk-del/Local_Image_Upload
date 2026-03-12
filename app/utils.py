from __future__ import annotations

import base64
import io
import ipaddress
import os
import re
import socket
import sys
import webbrowser
from pathlib import Path

import qrcode

VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".avi"}


def sanitize_stem(value: str) -> str:
    stem = value.strip().lower()
    stem = re.sub(r"\s+", "-", stem)
    stem = re.sub(r"[^a-z0-9._-]", "", stem)
    stem = re.sub(r"-+", "-", stem).strip("-._")
    return stem or "image"


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_local_client_host(client_host: str | None, local_ip: str) -> bool:
    if not client_host:
        return False

    if client_host == "localhost":
        return True

    try:
        address = ipaddress.ip_address(client_host)
    except ValueError:
        return False

    return address.is_loopback or client_host == local_ip


def detect_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
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


def open_directory_in_file_browser(path: Path) -> None:
    resolved = path.resolve()
    if sys.platform.startswith("win"):
        os.startfile(str(resolved))  # nosec B606
        return

    webbrowser.open(resolved.as_uri())


def list_uploaded_images(
    upload_dir: Path, allowed_extensions: set[str]
) -> list[dict[str, str | bool]]:
    images: list[dict[str, str | bool]] = []
    for image_path in sorted(upload_dir.rglob("*"), reverse=True):
        extension = image_path.suffix.lower()
        if not image_path.is_file() or extension not in allowed_extensions:
            continue

        relative_path = image_path.relative_to(upload_dir).as_posix()
        images.append(
            {
                "name": image_path.name,
                "relative_path": relative_path,
                "url": f"/uploads/{relative_path}",
                "is_video": extension in VIDEO_EXTENSIONS,
            }
        )

    return images


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
