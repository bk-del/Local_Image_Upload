# Handoff for another LLM

## Purpose

This repository is a local FastAPI image uploader intended for same-Wi-Fi phone-to-computer transfer. The desktop page shows a QR code that points to the LAN URL. The phone opens that page in a browser, selects multiple images, optionally renames each one, and uploads them to the host machine.

## What has already been created

- A working FastAPI app entrypoint in `app/main.py`
- A settings object in `app/config.py`
- Helper utilities in `app/utils.py`
- A Jinja2 HTML template in `templates/index.html`
- Mobile-friendly styling in `static/style.css`
- Frontend upload and preview logic in `static/app.js`
- Pytest coverage for routes and helpers
- Pre-commit hooks for Ruff, Black, isort, and Bandit
- GitHub Actions CI for lint, formatting, security scanning, and tests
- `start.sh` and `start.bat` for one-command launch
- A prompt file for spinning up the same project with another LLM

## Current behavior

- The app starts on `0.0.0.0:8000`
- The desktop browser opens `http://127.0.0.1:8000`
- The page shows the local network URL and QR code
- Uploads are saved to `uploads/YYYY-MM-DD/`
- Filenames are sanitized
- Collisions are resolved with suffixes like `_1`
- Only image extensions in the allowlist are accepted
- Oversized files are rejected

## Important files

- `app/main.py`: routes and application startup
- `app/utils.py`: IP detection, QR creation, sanitization, collision-safe naming
- `templates/index.html`: server-rendered page
- `static/app.js`: previews, rename inputs, upload request flow
- `tests/test_app.py`: route and upload tests
- `tests/test_utils.py`: helper tests
- `pyproject.toml`: runtime and dev dependencies plus tool configuration
- `.pre-commit-config.yaml`: local guardrails
- `.github/workflows/ci.yml`: CI pipeline

## Likely next improvements

- Add PyInstaller packaging support and executable build docs
- Add configurable port and upload directory via environment variables
- Add drag-and-drop image ordering
- Add better HEIC handling on desktop preview edge cases
- Add integration tests for browser behavior if needed

## Constraints to preserve

- Keep the stack simple: FastAPI plus plain HTML, CSS, and JavaScript
- Keep it local-only and same-Wi-Fi focused
- Preserve the QR code workflow
- Preserve one-command launch simplicity
- Avoid overengineering with React, auth, or databases unless requirements change
