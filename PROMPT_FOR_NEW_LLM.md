Build a complete working local web app using FastAPI for the backend and plain HTML, CSS, and JavaScript for the frontend.

Goal:
Create a local Wi-Fi image transfer app that runs on a computer and is usable from a phone browser on the same Wi-Fi network. The user must be able to open the page on the desktop, scan a QR code with the phone, open the page in the phone browser, select multiple images, optionally rename each image before upload, and save them directly into a folder on the computer.

Core product requirements:
1. The app must run locally on the computer.
2. The app must bind to the local network, not just localhost.
3. The desktop page must display a QR code for the phone URL.
4. The frontend must support selecting multiple image files.
5. Each selected image must show a preview.
6. Each selected image must have an optional custom filename field.
7. If a custom filename is blank, the app must use the original file stem.
8. The original file extension must be preserved.
9. Filenames must be sanitized safely.
10. Duplicate names must never overwrite existing files. Append suffixes like _1, _2, and so on.
11. Save files into date-based subfolders such as uploads/YYYY-MM-DD/.
12. Restrict uploads to image files only.
13. Enforce a configurable file size limit.
14. Show success and error messages clearly in the UI.
15. Keep the UI simple, clean, and mobile friendly.
16. The app should open the desktop browser automatically on launch if practical.

Packaging and run requirements:
1. The developer workflow should use uv with pyproject.toml and a lockfile.
2. Running the app should be possible with a single terminal command.
3. Provide start.sh and start.bat convenience launchers.
4. Structure the project so it can later be packaged into an executable with PyInstaller.
5. Do not use React, a database, authentication, or cloud services.

Code quality and automation requirements:
1. Configure Ruff, Black, isort, and Bandit.
2. Add pre-commit hooks so these run before commits.
3. Add pytest unit tests for filename sanitization, duplicate handling, the index route, and file upload behavior.
4. Add GitHub Actions CI to run lint, security checks, formatting checks, and tests on push and pull request.
5. Use readable code with minimal but useful comments.
6. Do not leave placeholders or pseudocode.

Expected project structure:
- app/__init__.py
- app/config.py
- app/main.py
- app/utils.py
- templates/index.html
- static/style.css
- static/app.js
- tests/test_app.py
- tests/test_utils.py
- .github/workflows/ci.yml
- .pre-commit-config.yaml
- .gitignore
- .python-version
- pyproject.toml
- README.md
- start.sh
- start.bat

Output format:
1. Show the full folder tree first.
2. Provide the complete contents of every file.
3. Explain how the single-command run flow works.
4. Explain how to install dev tooling and run the checks.
5. Explain how to test the phone QR flow.
6. End with a concise explanation of how the project is organized so another LLM can continue from it immediately.

Prioritize correctness, simplicity, completeness, and local reliability over fancy design.
