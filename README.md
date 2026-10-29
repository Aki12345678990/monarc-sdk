# analyzer_core

analyzer_core is a static analyzer for Android APK files. It checks the archive, reads package and SDK metadata, and writes a JSON report and a Markdown report.

It does not execute APK code. It does not produce a composite score, a 0–100 score, a tier, or a malware verdict.

## Current state

D and N implemented and parity-validated against the frozen v2 pipeline; A unavailable (API map not finalised); P and M not implemented (no v2 definition); report shows raw permissions and raw manifest facts. Schema 1.1.0 adds a univariate corpus comparison (percentile and histogram per metric; no pairing of indicators).

## Windows setup

```
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m pip install -e .
```

## CLI

```
analyzer analyze <apk_path> --out <dir>
analyzer analyze <apk_path> --json
analyzer verify-reference
analyzer version
analyzer schema
```

`python -m analyzer_core` accepts the same commands.

`analyze --out` writes `<sha256>.json` and `<sha256>.md` in the given directory. `--json` prints the JSON report to stdout and does not write those files. `verify-reference` prints `OK`, `MISMATCH`, or `EMPTY`. `version` prints the analyzer_core version and the installed androguard version.

Exit codes:

- 0: the command finished and, for `analyze`, the report status is ok
- 2: the file was rejected at intake
- 3: parse failed or timed out
- 1: internal error
- 4: reference data verification failed

## androguard pin

androguard is pinned at 3.3.5 so measurements stay comparable with the research corpus.

## Tests

```
.venv\Scripts\python -m pytest -q
```

Tests build synthetic ZIP archives in a temporary directory. They do not use APK files.

`analyzer schema` prints the JSON Schema of the Report model. The web app generates its TypeScript types from it.

## Web app (local)

Three local processes:

- **API** (`src/analyzer_service/api.py`, FastAPI on `http://127.0.0.1:8000`). The browser creates a job with `POST /api/jobs` and then uploads the APK bytes directly to `PUT /api/jobs/{id}/upload`. The API streams the upload to `var/staging/{job_id}.part`, renames it, and runs `analyzer_core.intake.validate()`. A rejected file is deleted immediately. If a report already exists for the same SHA-256, engine version and reference manifest, the job is marked done from that cached report and the file is deleted. Otherwise the job is queued.
- **Worker** (`src/analyzer_service/worker.py`). It leases one queued job at a time from SQLite (`var/jobs.sqlite`, WAL mode), calls `analyzer_core.pipeline.analyze()`, and writes the report JSON to `var/reports/`. It deletes the staged APK once the job is done or failed.
- **Next.js** (`web/`, `http://localhost:3000`). It renders the upload page, polls job status and renders the report. It never receives APK bytes. Report types in `web/src/lib/report-types.ts` are generated from `analyzer schema` (`npm run gen:types`).

Setup:

```
.venv\Scripts\python -m pip install -r requirements-service.txt
.venv\Scripts\python -m pip install -e .
cd web
npm install
copy .env.example .env.local
```

Run (three terminals, or `scripts\dev.ps1` to open all three):

```
.venv\Scripts\python -m analyzer_service api
.venv\Scripts\python -m analyzer_service worker
cd web && npm run dev
```

Service environment variables (prefix `ANALYZER_SVC_`):

| Variable | Default |
| --- | --- |
| `ANALYZER_SVC_VAR_DIR` | `<repo>\var` |
| `ANALYZER_SVC_DB_PATH` | `<VAR_DIR>\jobs.sqlite` |
| `ANALYZER_SVC_MAX_UPLOAD_BYTES` | analyzer_core `MAX_APK_BYTES` (300 MiB) |
| `ANALYZER_SVC_JOB_TIMEOUT_S` | `900` (the worker sets `ANALYZER_PARSE_TIMEOUT_S` to this) |
| `ANALYZER_SVC_LEASE_S` | `1200` |
| `ANALYZER_SVC_MAX_ATTEMPTS` | `2` |
| `ANALYZER_SVC_UPLOAD_TTL_S` | `900` |
| `ANALYZER_SVC_CORS_ORIGINS` | `http://localhost:3000` (comma-separated) |

Web environment variable: `NEXT_PUBLIC_API_BASE` (default `http://localhost:8000`) in `web\.env.local`.

Retention: uploaded APKs are deleted after analysis, rejection or failure. Upload slots that receive no file within `UPLOAD_TTL_S` expire, and any partial file is deleted. Reports are kept in `var/reports/`, keyed `{sha256}__{engine_version}__{reference_manifest_sha256[:12]}.json`.

The UI shows indicators exactly as the report states them. It shows no composite score, rating, tier or malware verdict.

Deployment (R2, Postgres, Railway, Vercel, Docker) is a separate step.
