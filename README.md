# Local Image Drop

A local FastAPI app for sending images from a phone browser to a computer on the same Wi-Fi network. The page shows a QR code, previews selected images, supports optional per-image renaming, and saves files into dated upload folders.

## What is included

- FastAPI backend
- Plain HTML, CSS, and JavaScript frontend
- QR code display for quick phone access
- Safe filename sanitization and collision handling
- Date-based upload folders
- Unit tests with pytest
- Pre-commit hooks for Ruff, Black, isort, and Bandit
- GitHub Actions CI
- One-command launch scripts for Windows and macOS/Linux
- uv-compatible project metadata; generate uv.lock in a networked environment with `uv lock` or `uv sync`

## Project layout

```text
local-image-drop/
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ main.py
│  └─ utils.py
├─ static/
│  ├─ app.js
│  └─ style.css
├─ templates/
│  └─ index.html
├─ tests/
│  ├─ conftest.py
│  ├─ test_app.py
│  └─ test_utils.py
├─ .gitignore
├─ .pre-commit-config.yaml
├─ .python-version
├─ LLM_HANDOFF.md
├─ PROMPT_FOR_NEW_LLM.md
├─ README.md
├─ pyproject.toml
├─ start.bat
└─ start.sh
```

## Run locally

### Preferred

```bash
uv run python -m app.main
```

### Convenience scripts

```bash
./start.sh
```

or on Windows:

```bat
start.bat
```

The app opens in your desktop browser at `http://127.0.0.1:8000` and shows a QR code for the phone URL.

## Install development tooling

```bash
uv sync --group dev
uv run pre-commit install
```

## Run checks manually

```bash
uv run ruff check .
uv run black --check .
uv run isort --check-only .
uv run bandit -c pyproject.toml -r app
uv run pytest
```

## Phone workflow

1. Start the app on the computer.
2. Open the desktop browser page.
3. Scan the QR code with the phone.
4. Select multiple images on the phone.
5. Optionally type a custom filename for each image.
6. Upload the files.
7. Find the files in `uploads/YYYY-MM-DD/`.

## Notes

- The app listens on `0.0.0.0` so it is reachable on the local network.
- A local firewall prompt may appear on first run. Allow local network access.
- The upload directory is created automatically.
