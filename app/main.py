from __future__ import annotations

import datetime as dt
import webbrowser
from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import DEFAULT_SETTINGS, Settings
from app.utils import (
    dated_upload_dir,
    detect_local_ip,
    ensure_directory,
    get_extension,
    is_local_client_host,
    list_uploaded_images,
    make_qr_data_uri,
    open_directory_in_file_browser,
    sanitize_stem,
    unique_path,
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
UPLOAD_STREAM_CHUNK_SIZE = 1024 * 1024


def is_local_machine_request(request: Request, local_ip: str | None = None) -> bool:
    if request.client is None:
        return False

    resolved_local_ip = local_ip or detect_local_ip()
    return is_local_client_host(request.client.host, resolved_local_ip)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or DEFAULT_SETTINGS
    ensure_directory(app_settings.upload_dir)

    app = FastAPI(title=app_settings.app_name)
    app.state.settings = app_settings
    app.state.upload_event_id = 0
    app.state.latest_upload_event = None
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
    app.mount("/uploads", StaticFiles(directory=str(app_settings.upload_dir)), name="uploads")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        local_ip = detect_local_ip()
        network_url = f"http://{local_ip}:{app_settings.port}"
        qr_data_uri = make_qr_data_uri(network_url)
        can_open_uploads = is_local_machine_request(request, local_ip)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "app_name": app_settings.app_name,
                "network_url": network_url,
                "qr_data_uri": qr_data_uri,
                "max_upload_mb": app_settings.max_upload_bytes // (1024 * 1024),
                "can_open_uploads": can_open_uploads,
            },
        )

    @app.get("/gallery", response_class=HTMLResponse)
    async def gallery(request: Request) -> HTMLResponse:
        images = list_uploaded_images(app_settings.upload_dir, app_settings.allowed_extensions)

        return TEMPLATES.TemplateResponse(
            request=request,
            name="gallery.html",
            context={"app_name": app_settings.app_name, "images": images},
        )

    @app.post("/open-uploads")
    async def open_uploads_folder(request: Request) -> JSONResponse:
        if not is_local_machine_request(request):
            raise HTTPException(
                status_code=403,
                detail="This action is only available on this computer.",
            )

        uploads_path = ensure_directory(app_settings.upload_dir).resolve()
        try:
            open_directory_in_file_browser(uploads_path)
        except OSError as exc:
            raise HTTPException(status_code=500, detail="Could not open uploads folder.") from exc

        return JSONResponse({"message": "Opened uploads folder.", "path": str(uploads_path)})

    @app.get("/upload-status")
    async def upload_status(request: Request) -> JSONResponse:
        if not is_local_machine_request(request):
            raise HTTPException(
                status_code=403,
                detail="This action is only available on this computer.",
            )

        return JSONResponse({"latest_upload": app.state.latest_upload_event})

    @app.post("/upload")
    async def upload_images(
        request: Request,
        files: Annotated[list[UploadFile], File(...)],
        names: Annotated[list[str] | None, Form()] = None,
    ) -> JSONResponse:
        resolved_names = names or []
        saved_files: list[dict[str, str | int]] = []
        target_dir = dated_upload_dir(app_settings.upload_dir, dt.date.today().isoformat())

        for index, uploaded_file in enumerate(files):
            extension = get_extension(uploaded_file.filename or "")
            if extension not in app_settings.allowed_extensions:
                await uploaded_file.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for {uploaded_file.filename or 'unknown file'}.",
                )

            custom_name = resolved_names[index].strip() if index < len(resolved_names) else ""
            desired_stem = custom_name or Path(uploaded_file.filename or "image").stem
            destination = unique_path(target_dir, sanitize_stem(desired_stem), extension)
            size_bytes = 0
            try:
                with destination.open("wb") as output_file:
                    while True:
                        chunk = await uploaded_file.read(UPLOAD_STREAM_CHUNK_SIZE)
                        if not chunk:
                            break

                        size_bytes += len(chunk)
                        if size_bytes > app_settings.max_upload_bytes:
                            raise HTTPException(
                                status_code=400,
                                detail=(
                                    f"{uploaded_file.filename or 'File'} exceeds the size limit."
                                ),
                            )
                        output_file.write(chunk)
            except HTTPException:
                destination.unlink(missing_ok=True)
                raise
            except OSError as exc:
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=500,
                    detail="Could not save uploaded file.",
                ) from exc
            finally:
                await uploaded_file.close()
            relative_path = destination.relative_to(app_settings.upload_dir).as_posix()

            saved_files.append(
                {
                    "original_name": uploaded_file.filename or "",
                    "saved_name": destination.name,
                    "relative_path": relative_path,
                    "preview_url": f"/uploads/{relative_path}",
                    "size_bytes": size_bytes,
                }
            )

        uploaded_count = len(saved_files)
        saved_folder = target_dir.relative_to(app_settings.upload_dir.parent).as_posix()
        response_payload = {
            "message": f"Uploaded {uploaded_count} file(s).",
            "uploaded_count": uploaded_count,
            "saved_folder": saved_folder,
            "saved_files": saved_files,
            "target_directory": str(target_dir),
        }
        app.state.upload_event_id += 1
        app.state.latest_upload_event = {
            "event_id": app.state.upload_event_id,
            "timestamp": dt.datetime.now(dt.UTC).isoformat(),
            "source_host": request.client.host if request.client else "unknown",
            "message": response_payload["message"],
            "uploaded_count": uploaded_count,
            "saved_folder": saved_folder,
            "saved_files": saved_files,
        }

        return JSONResponse(response_payload)

    return app


app = create_app()


def run() -> None:
    settings = DEFAULT_SETTINGS
    if settings.open_browser_on_start:
        webbrowser.open(f"http://127.0.0.1:{settings.port}")
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    run()
