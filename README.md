# Local Image Drop

Simple local tool to send photos from a phone to a computer on the same Wi-Fi.

- Phone view: **Send Photos to Computer**
- Computer view: QR code, **Open Photo Folder**, **View Uploaded Photos**, and live upload confirmation

No cloud, no database, no accounts.

## Safety first

This app has **no authentication** and uses local HTTP.

- Use only on trusted home Wi-Fi.
- Do not use on public/shared Wi-Fi.
- Do not expose this app to the internet or port-forward it.
- Stop the app when done.

## Setup (once)

From the repo root:

```bash
uv sync --group dev
```

## Run (every time)

From the repo root:

```bash
uv run python -m app.main
```

The browser opens automatically on the computer.

## Windows shortcuts

- First time: `setup.bat`
- Each run: `run.bat`

## How to use

1. Start the app on the computer.
2. On the computer page, scan the QR code with your phone.
3. On the phone page, tap **Choose Photos**.
4. (Optional) rename photos.
5. Tap **Send Photos to Computer**.
6. On the computer page, watch the confirmation panel update automatically.

## Where files go

Uploaded files are saved to:

- `uploads/YYYY-MM-DD/`

Examples:

- `uploads/2026-03-12/photo.jpg`
- `uploads/2026-03-12/photo_1.jpg` (name collision)

Rules:

- image files only
- extension preserved
- filename sanitized
- duplicate names get `_1`, `_2`, ...

## Computer actions

- **Open Photo Folder**: opens top-level `uploads/` on the computer
- **View Uploaded Photos**: opens gallery (`/gallery`) of photos stored on the computer

`Open Photo Folder` is local-only and cannot be triggered by phone clients.

## Dev checks

```bash
uv run ruff check .
uv run black --check .
uv run isort --check-only .
uv run bandit -c pyproject.toml -r app
uv run pytest
```
