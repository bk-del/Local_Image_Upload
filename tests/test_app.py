from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def build_client(tmp_path: Path) -> TestClient:
    settings = Settings(upload_dir=tmp_path / "uploads", open_browser_on_start=False)
    app = create_app(settings)
    return TestClient(app, client=("127.0.0.1", 50000))


def test_index_page_renders_qr_and_phone_url(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    client = build_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "http://192.168.1.50:8000" in response.text
    assert "data:image/png;base64" in response.text
    assert "Open Photo Folder" in response.text
    assert "View Uploaded Photos" in response.text
    assert "Scan to send photos from your phone" in response.text
    assert "Waiting for photos from phone." in response.text
    assert 'id="upload-form"' not in response.text


def test_index_hides_open_folder_button_for_remote_clients(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    app = create_app(Settings(upload_dir=tmp_path / "uploads", open_browser_on_start=False))
    client = TestClient(app, client=("203.0.113.20", 50000))

    response = client.get("/")

    assert response.status_code == 200
    assert "Send Photos to Computer" in response.text
    assert "Choose Photos" in response.text
    assert 'id="upload-form"' in response.text
    assert "Open Photo Folder" not in response.text
    assert "View Photos Stored on Computer" in response.text


def test_gallery_page_shows_uploaded_images(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    upload_day_dir = tmp_path / "uploads" / "2026-03-11"
    upload_day_dir.mkdir(parents=True)
    (upload_day_dir / "beach.png").write_bytes(b"fake-image")
    (upload_day_dir / "notes.txt").write_bytes(b"text-file")

    client = build_client(tmp_path)
    response = client.get("/gallery")

    assert response.status_code == 200
    assert "beach.png" in response.text
    assert "2026-03-11/beach.png" in response.text
    assert "/uploads/2026-03-11/beach.png" in response.text
    assert "notes.txt" not in response.text


def test_upload_status_route_is_local_only(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    app = create_app(Settings(upload_dir=tmp_path / "uploads", open_browser_on_start=False))
    local_client = TestClient(app, client=("127.0.0.1", 50000))
    remote_client = TestClient(app, client=("203.0.113.20", 50000))

    local_response = local_client.get("/upload-status")
    remote_response = remote_client.get("/upload-status")

    assert local_response.status_code == 200
    assert local_response.json()["latest_upload"] is None
    assert remote_response.status_code == 403


def test_upload_status_updates_after_remote_upload(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    app = create_app(Settings(upload_dir=tmp_path / "uploads", open_browser_on_start=False))
    local_client = TestClient(app, client=("127.0.0.1", 50000))
    phone_client = TestClient(app, client=("203.0.113.20", 50000))

    upload_response = phone_client.post(
        "/upload",
        files=[("files", ("beach.png", b"fake-image-bytes", "image/png"))],
        data={"names": "vacation-shot"},
    )
    status_response = local_client.get("/upload-status")

    assert upload_response.status_code == 200
    assert status_response.status_code == 200
    latest_upload = status_response.json()["latest_upload"]
    assert latest_upload["event_id"] == 1
    assert latest_upload["source_host"] == "203.0.113.20"
    assert latest_upload["uploaded_count"] == 1
    assert latest_upload["saved_folder"].startswith("uploads/")
    assert latest_upload["saved_files"][0]["saved_name"] == "vacation-shot.png"


def test_open_uploads_folder_is_local_only(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.main.detect_local_ip", lambda: "192.168.1.50")
    opened_path: dict[str, Path] = {}

    def fake_open(path: Path) -> None:
        opened_path["path"] = path

    monkeypatch.setattr("app.main.open_directory_in_file_browser", fake_open)
    local_client = build_client(tmp_path)
    remote_client = TestClient(
        create_app(Settings(upload_dir=tmp_path / "uploads", open_browser_on_start=False)),
        client=("203.0.113.20", 50000),
    )

    local_response = local_client.post("/open-uploads")
    remote_response = remote_client.post("/open-uploads")

    assert local_response.status_code == 200
    assert local_response.json()["message"] == "Opened uploads folder."
    assert opened_path["path"] == (tmp_path / "uploads").resolve()
    assert remote_response.status_code == 403
    assert "only available on this computer" in remote_response.json()["detail"]


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
    assert payload["uploaded_count"] == 1
    assert payload["saved_folder"].startswith("uploads/")
    assert payload["saved_files"][0]["relative_path"].endswith(f"/{saved_name}")
    assert payload["saved_files"][0]["preview_url"].endswith(f"/{saved_name}")

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
