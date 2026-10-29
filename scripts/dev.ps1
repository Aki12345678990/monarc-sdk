# Starts the three local processes of the web layer, each in its own PowerShell window:
#   1. API     - python -m analyzer_service api     (FastAPI on http://127.0.0.1:8000)
#   2. Worker  - python -m analyzer_service worker  (leases queued jobs, runs analyzer_core)
#   3. Web     - npm run dev in web\                (Next.js on http://localhost:3000)
# Close a window (or press Ctrl+C in it) to stop that process.
# Prerequisites: .venv with requirements-service.txt and `pip install -e .`; `npm install` in web\.

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$web = Join-Path $root "web"

if (-not (Test-Path $python)) {
    Write-Error "Python virtual environment not found at $python"
    exit 1
}

# API: receives uploads directly from the browser and serves job status and reports.
Start-Process powershell -WorkingDirectory $root -ArgumentList @(
    "-NoExit", "-Command", "& '$python' -m analyzer_service api"
)

# Worker: one job at a time; deletes each staged APK once its job reaches a terminal state.
Start-Process powershell -WorkingDirectory $root -ArgumentList @(
    "-NoExit", "-Command", "& '$python' -m analyzer_service worker"
)

# Next.js dev server: renders the upload page and the report view. It never receives APK bytes.
Start-Process powershell -WorkingDirectory $web -ArgumentList @(
    "-NoExit", "-Command", "npm run dev"
)

Write-Host "Started API (http://127.0.0.1:8000), worker, and web (http://localhost:3000)."
