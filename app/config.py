from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    app_name: str = "Local Image Drop"
    host: str = "0.0.0.0"
    port: int = 8000
    upload_dir: Path = Path("uploads")
    max_upload_bytes: int = 15 * 1024 * 1024
    allowed_extensions: set[str] = field(
        default_factory=lambda: {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}
    )
    open_browser_on_start: bool = True


DEFAULT_SETTINGS = Settings()
