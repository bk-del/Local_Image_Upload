# Local Image Drop

Simple local tool to send photos/videos from a phone to a computer on the same Wi-Fi.

- Phone view: **Send Photos/Videos to Computer**
- Computer view: QR code, **Open Photo Folder**, **View Uploaded Photos**, and live upload confirmation
- Separate page: **Send Files to Phone** (isolated from phone-to-computer flow)
- Live top-right status on both pages: shows whether the other device is currently connected

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

### Phone -> Computer

1. Start the app on the computer.
2. On the computer page, scan the QR code with your phone.
3. On the phone page, tap **Choose Photos/Videos**.
4. (Optional) rename files.
5. Tap **Send Photos/Videos to Computer**.
6. On the computer page, watch the confirmation panel update automatically.
7. Check the top-right status: **Connected** means a phone is actively on the app.

### Computer -> Phone (separate screen)

1. On the computer main page, click **Send Files to Phone**.
2. Click **Choose Files on Computer** and select photos/videos from any folder.
3. (Optional) rename files.
4. Click **Send to Phone**.
5. Use the page QR code (or URL) on the phone to open `/to-phone`.
6. On the phone `/to-phone` page, tap **Open / Download** on a file.
7. Both screens show top-right live connection status.
8. **Send to Phone** means files become available at `/to-phone`; the phone user still taps **Open / Download**.

## Where files go

Phone -> computer uploads are saved to:

- `uploads/YYYY-MM-DD/`

Computer -> phone sent files are saved to:

- `uploads/to-phone/YYYY-MM-DD/`

Examples:

- `uploads/2026-03-12/photo.jpg`
- `uploads/2026-03-12/photo_1.jpg` (name collision)
- `uploads/2026-03-12/video.mp4`
- `uploads/to-phone/2026-03-12/video.mp4`

Rules:

- image + video files
- max size per file: 500 MB
- extension preserved
- filename sanitized
- duplicate names get `_1`, `_2`, ...
- allowed video formats: `.mp4`, `.mov`, `.m4v`, `.webm`, `.avi`

## Computer actions

- **Open Photo Folder**: opens top-level `uploads/` on the computer
- **View Uploaded Photos**: opens gallery (`/gallery`) of photos stored on the computer
- **Send Files to Phone**: opens isolated page to send files to the phone download page (`/to-phone`)

`Open Photo Folder` is local-only and cannot be triggered by phone clients.

## Dev checks

```bash
uv run ruff check .
uv run black --check .
uv run isort --check-only .
uv run bandit -c pyproject.toml -r app
uv run pytest
```
