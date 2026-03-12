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
    make_qr_data_uri,
    sanitize_stem,
    unique_path,
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or DEFAULT_SETTINGS
    ensure_directory(app_settings.upload_dir)

    app = FastAPI(title=app_settings.app_name)
    app.state.settings = app_settings
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        local_ip = detect_local_ip()
        network_url = f"http://{local_ip}:{app_settings.port}"
        qr_data_uri = make_qr_data_uri(network_url)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "app_name": app_settings.app_name,
                "network_url": network_url,
                "qr_data_uri": qr_data_uri,
                "max_upload_mb": app_settings.max_upload_bytes // (1024 * 1024),
            },
        )

    @app.post("/upload")
    async def upload_images(
        files: Annotated[list[UploadFile], File(...)],
        names: list[str] = Form(default=[]),
    ) -> JSONResponse:
        saved_files: list[dict[str, str | int]] = []
        target_dir = dated_upload_dir(app_settings.upload_dir, dt.date.today().isoformat())

        for index, uploaded_file in enumerate(files):
            extension = get_extension(uploaded_file.filename or "")
            if extension not in app_settings.allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for {uploaded_file.filename or 'unknown file'}.",
                )

            content = await uploaded_file.read()
            if len(content) > app_settings.max_upload_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=f"{uploaded_file.filename or 'File'} exceeds the size limit.",
                )

            custom_name = names[index].strip() if index < len(names) else ""
            desired_stem = custom_name or Path(uploaded_file.filename or "image").stem
            destination = unique_path(target_dir, sanitize_stem(desired_stem), extension)
            destination.write_bytes(content)

            saved_files.append(
                {
                    "original_name": uploaded_file.filename or "",
                    "saved_name": destination.name,
                    "relative_path": str(destination.relative_to(app_settings.upload_dir.parent)),
                    "size_bytes": len(content),
                }
            )

        return JSONResponse(
            {
                "message": f"Saved {len(saved_files)} image(s).",
                "saved_files": saved_files,
                "target_directory": str(target_dir),
            }
        )

    return app


app = create_app()


def run() -> None:
    settings = DEFAULT_SETTINGS
    if settings.open_browser_on_start:
        webbrowser.open(f"http://127.0.0.1:{settings.port}")
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    run()
