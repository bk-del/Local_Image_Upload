from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def build_client(tmp_path: Path) -> TestClient:
    settings = Settings(upload_dir=tmp_path / "uploads", open_browser_on_start=False)
    app = create_app(settings)
    return TestClient(app)


def test_index_page_renders_qr_and_phone_url(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    client = build_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "http://192.168.1.50:8000" in response.text
    assert "data:image/png;base64" in response.text


def test_upload_saves_file_into_dated_folder(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    client = build_client(tmp_path)

    response = client.post(
        "/upload",
        files=[("files", ("beach.png", b"fake-image-bytes", "image/png"))],
        data={"names": "vacation-shot"},
    )

    assert response.status_code == 200
    payload = response.json()
    saved_name = payload["saved_files"][0]["saved_name"]
    assert saved_name == "vacation-shot.png"

    dated_directories = list((tmp_path / "uploads").iterdir())
    assert len(dated_directories) == 1
    saved_file = dated_directories[0] / saved_name
    assert saved_file.exists()


def test_upload_uses_suffix_for_name_collision(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    client = build_client(tmp_path)

    first = client.post(
        "/upload",
        files=[("files", ("image.jpg", b"first", "image/jpeg"))],
        data={"names": "trip"},
    )
    second = client.post(
        "/upload",
        files=[("files", ("image.jpg", b"second", "image/jpeg"))],
        data={"names": "trip"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["saved_files"][0]["saved_name"] == "trip_1.jpg"


def test_upload_rejects_invalid_extension(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    client = build_client(tmp_path)

    response = client.post(
        "/upload",
        files=[("files", ("notes.txt", b"not-an-image", "text/plain"))],
        data={"names": "notes"},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_rejects_oversized_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    settings = Settings(
        upload_dir=tmp_path / "uploads",
        open_browser_on_start=False,
        max_upload_bytes=4,
    )
    client = TestClient(create_app(settings))

    response = client.post(
        "/upload",
        files=[("files", ("large.png", b"12345", "image/png"))],
        data={"names": "large"},
    )

    assert response.status_code == 400
    assert "size limit" in response.json()["detail"]
