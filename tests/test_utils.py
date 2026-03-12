from pathlib import Path

from app.utils import (
    dated_upload_dir,
    get_extension,
    is_local_client_host,
    list_uploaded_images,
    sanitize_stem,
    unique_path,
)


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


def test_dated_upload_dir_creates_nested_folder(tmp_path: Path) -> None:
    target = dated_upload_dir(tmp_path / "uploads", "2026-03-11")

    assert target.exists()
    assert target.is_dir()
    assert target.name == "2026-03-11"


def test_is_local_client_host_checks_loopback_and_lan() -> None:
    local_ip = "192.168.1.50"

    assert is_local_client_host("127.0.0.1", local_ip) is True
    assert is_local_client_host("localhost", local_ip) is True
    assert is_local_client_host(local_ip, local_ip) is True
    assert is_local_client_host("203.0.113.20", local_ip) is False


def test_list_uploaded_images_returns_recursive_image_paths_only(tmp_path: Path) -> None:
    upload_dir = tmp_path / "uploads"
    (upload_dir / "2026-03-10").mkdir(parents=True)
    (upload_dir / "2026-03-10" / "cat.jpg").write_bytes(b"img")
    (upload_dir / "2026-03-10" / "notes.txt").write_bytes(b"text")

    images = list_uploaded_images(upload_dir, {".jpg", ".png"})

    assert len(images) == 1
    assert images[0]["name"] == "cat.jpg"
    assert images[0]["relative_path"] == "2026-03-10/cat.jpg"
    assert images[0]["url"] == "/uploads/2026-03-10/cat.jpg"
