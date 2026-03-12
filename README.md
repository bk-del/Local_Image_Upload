# Local Image Drop

Local Image Drop is a small local-network photo uploader:
- Run it on your computer.
- Scan a QR code from your phone on the same Wi-Fi.
- Upload one or more photos from the phone browser.
- Optionally rename each photo before upload.
- Files are saved to `uploads/YYYY-MM-DD/`.

No cloud services, no database, no auth setup.

## Safety warning (important)

This app is intentionally minimal and has no login or protection layer.

- No authentication: anyone on the same network who can reach the URL can use it.
- No HTTPS/TLS: traffic is plain local HTTP.
- No user accounts or permission controls.

Use it only on a trusted home network.

Do:
- use your private home Wi-Fi
- run only when needed
- stop the app when finished

Do not:
- use on public Wi-Fi (coffee shops, hotels, airports)
- expose this app to the internet
- port-forward router traffic to this app

## Setup once

From the repo root:

```bash
uv sync --group dev
```

## Run each time

From the repo root:

```
bash
uv run python -m app.main
```

When it starts, it opens your desktop browser automatically.

## Windows wrappers

If you prefer double-click scripts on Windows:

- One-time setup: `setup.bat`
- Run app: `run.bat`

(`start.bat` is kept as a compatibility wrapper to `run.bat`.)

## Phone usage on same Wi-Fi

1. Start the app on the computer.
2. Desktop page opens and shows a QR code and phone URL.
3. Scan the QR code from your phone camera.
4. Select photos.
5. Optionally enter custom names.
6. Tap upload.

The QR code points to your computer's local LAN URL (for example `http://192.168.1.50:8000`).

For safety, make sure both devices are on your trusted home Wi-Fi (not a public/shared network).

## Where photos are saved

Photos are saved under top-level `uploads/` with date-based folders:

- `uploads/2026-03-11/photo.jpg`
- `uploads/2026-03-11/photo_1.jpg` (collision-safe naming)

Behavior:
- extension preserved
- filename sanitized
- duplicate names get `_1`, `_2`, etc.
- image files only

## Desktop page actions

Main page is intentionally simple:
- Select photos
- Optional photo names
- Upload photos
- `Open Photo Folder` (desktop-local access only)
- `View Uploaded Photos` (gallery page)
- Upload confirmation panel with:
  - success message
  - upload count
  - saved folder path
  - thumbnails of newly uploaded photos
  - final saved filenames

`Open Photo Folder` opens the top-level `uploads/` folder in File Explorer (Windows). Remote phone clients cannot trigger this route.

## Gallery page

`/gallery` shows uploaded photos recursively from `uploads/`:
- thumbnail preview
- saved filename
- relative subpath
- click to open full image in browser

## Quality checks

```bash
uv run ruff check .
uv run black --check .
uv run isort --check-only .
uv run bandit -c pyproject.toml -r app
uv run pytest
```

## Tooling included

- Ruff
- Black
- isort
- Bandit
- pytest
- pre-commit
- GitHub Actions CI
