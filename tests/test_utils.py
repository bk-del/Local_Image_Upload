from pathlib import Path

from app.utils import get_extension, sanitize_stem, unique_path


def test_sanitize_stem_normalizes_value() -> None:
    assert sanitize_stem("  My Summer Photo!!  ") == "my-summer-photo"


def test_sanitize_stem_falls_back_to_image() -> None:
    assert sanitize_stem("***") == "image"


def test_get_extension_returns_lowercase_suffix() -> None:
    assert get_extension("PIC.JPEG") == ".jpeg"


def test_unique_path_appends_counter_when_file_exists(tmp_path: Path) -> None:
    original = tmp_path / "sample.jpg"
    original.write_bytes(b"first")

    candidate = unique_path(tmp_path, "sample", ".jpg")

    assert candidate.name == "sample_1.jpg"
