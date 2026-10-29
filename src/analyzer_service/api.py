"""FastAPI job API: create job, stream upload, intake, job status, reports, health."""

import json
import threading
import time
import uuid
from datetime import datetime, timezone
from importlib.metadata import version as package_version

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from starlette.requests import ClientDisconnect

from analyzer_core import __version__ as engine_version
from analyzer_core.errors import AnalyzerError, ErrorCode
from analyzer_core.intake import validate
from analyzer_core.reference import verify
from analyzer_service.db import (
    AWAITING_UPLOAD,
    EXPIRED,
    Job,
    JobDB,
)
from analyzer_service.settings import Settings, load_settings
from analyzer_service.storage import (
    LocalStorage,
    Storage,
    current_report_key,
    is_valid_report_key,
)

_CHUNK_BYTES = 1024 * 1024
_CLEANUP_INTERVAL_S = 30.0


class CreateJobRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=4096)


def _iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def job_view(job: Job) -> dict:
    return {
        "job_id": job.id,
        "status": job.status,
        "error_code": job.error_code,
        "error_message": job.error_message,
        "sha256": job.sha256,
        "file_size": job.file_size,
        "created_at": _iso(job.created_at),
        "updated_at": _iso(job.updated_at),
        "report_url": f"/api/reports/{job.report_key}" if job.report_key else None,
    }


def _is_ok_report(payload: str | None) -> bool:
    if payload is None:
        return False
    try:
        return json.loads(payload).get("status") == "ok"
    except (ValueError, AttributeError):
        return False


def _valid_job_id(job_id: str) -> bool:
    try:
        return str(uuid.UUID(job_id)) == job_id
    except ValueError:
        return False


def create_app(
    settings: Settings | None = None,
    storage: Storage | None = None,
) -> FastAPI:
    settings = settings or load_settings()
    settings.var_dir.mkdir(parents=True, exist_ok=True)
    store: Storage = storage or LocalStorage(settings.var_dir)
    db = JobDB(settings.db_path, lease_s=settings.lease_s, max_attempts=settings.max_attempts)

    active_uploads: set[str] = set()
    active_lock = threading.Lock()
    cleanup_state = {"last": 0.0}
    cleanup_lock = threading.Lock()

    app = FastAPI(title="analyzer_service", version=engine_version)
    app.state.settings = settings
    app.state.db = db
    app.state.storage = store

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type"],
    )

    def run_cleanup() -> None:
        now = time.monotonic()
        with cleanup_lock:
            if cleanup_state["last"] and now - cleanup_state["last"] < _CLEANUP_INTERVAL_S:
                return
            cleanup_state["last"] = now
        with active_lock:
            busy = set(active_uploads)
        for job_id in db.expire_uploads(exclude=busy):
            store.delete_upload(job_id)

    @app.middleware("http")
    async def headers_and_cleanup(request: Request, call_next):
        await run_in_threadpool(run_cleanup)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    def get_job_or_404(job_id: str) -> Job:
        job = db.get_job(job_id) if _valid_job_id(job_id) else None
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found.")
        return job

    @app.post("/api/jobs")
    def create_job(body: CreateJobRequest) -> dict:
        job = db.create_job(body.filename, settings.upload_ttl_s)
        return {
            "job_id": job.id,
            "upload_url": f"/api/jobs/{job.id}/upload",
            "upload_method": "PUT",
            "max_bytes": settings.max_upload_bytes,
            "expires_at": _iso(job.upload_expires_at),
        }

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: str) -> dict:
        return job_view(get_job_or_404(job_id))

    def too_large(job_id: str) -> JSONResponse:
        store.delete_upload(job_id)
        db.mark_rejected(
            job_id,
            ErrorCode.E_TOO_LARGE.value,
            f"Upload exceeds {settings.max_upload_bytes} bytes.",
        )
        return JSONResponse(status_code=413, content={"detail": "Upload too large."})

    @app.put("/api/jobs/{job_id}/upload")
    async def upload(job_id: str, request: Request):
        job = await run_in_threadpool(get_job_or_404, job_id)
        if job.status == EXPIRED:
            raise HTTPException(status_code=410, detail="Upload window expired.")
        if job.status != AWAITING_UPLOAD:
            raise HTTPException(status_code=409, detail="Job is not awaiting upload.")
        if time.time() > job.upload_expires_at:
            db.mark_expired(job_id)
            store.delete_upload(job_id)
            raise HTTPException(status_code=410, detail="Upload window expired.")

        declared = request.headers.get("content-length")
        if declared is not None and declared.isdigit() and int(declared) > settings.max_upload_bytes:
            return too_large(job_id)

        with active_lock:
            if job_id in active_uploads:
                raise HTTPException(status_code=409, detail="Upload already in progress.")
            active_uploads.add(job_id)
        try:
            part = store.begin_upload(job_id)
            try:
                handle = open(part, "xb")
            except FileExistsError:
                raise HTTPException(status_code=409, detail="Upload already in progress.")

            total = 0
            exceeded = False
            buffer = bytearray()
            try:
                with handle:
                    async for chunk in request.stream():
                        total += len(chunk)
                        if total > settings.max_upload_bytes:
                            exceeded = True
                            break
                        buffer += chunk
                        while len(buffer) >= _CHUNK_BYTES:
                            await run_in_threadpool(handle.write, bytes(buffer[:_CHUNK_BYTES]))
                            del buffer[:_CHUNK_BYTES]
                    if not exceeded and buffer:
                        await run_in_threadpool(handle.write, bytes(buffer))
            except ClientDisconnect:
                store.delete_upload(job_id)
                return JSONResponse(status_code=400, content={"detail": "Upload interrupted."})
            except BaseException:
                store.delete_upload(job_id)
                raise

            if exceeded:
                return too_large(job_id)

            apk_path = store.finalize(job_id)
            try:
                accepted = await run_in_threadpool(validate, apk_path)
            except AnalyzerError as exc:
                store.delete_upload(job_id)
                db.mark_rejected(
                    job_id,
                    exc.code.value,
                    exc.message,
                    sha256=exc.sha256,
                    file_size=exc.file_size,
                )
                return job_view(get_job_or_404(job_id))
            except Exception as exc:
                store.delete_upload(job_id)
                db.mark_upload_failed(
                    job_id, ErrorCode.E_INTERNAL.value, f"{type(exc).__name__}: {exc}"
                )
                return job_view(get_job_or_404(job_id))

            key = current_report_key(accepted.sha256)
            cached = key if _is_ok_report(store.get_report(key)) else None
            updated = db.mark_uploaded(
                job_id,
                sha256=accepted.sha256,
                file_size=accepted.file_size,
                cached_report_key=cached,
            )
            if cached is not None or not updated:
                store.delete_upload(job_id)
            if not updated:
                raise HTTPException(status_code=409, detail="Job is not awaiting upload.")
            return job_view(get_job_or_404(job_id))
        finally:
            with active_lock:
                active_uploads.discard(job_id)

    @app.get("/api/reports/{report_key}")
    def get_report(report_key: str) -> Response:
        if not is_valid_report_key(report_key):
            raise HTTPException(status_code=404, detail="Report not found.")
        payload = store.get_report(report_key)
        if payload is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        return Response(content=payload, media_type="application/json")

    @app.get("/api/health")
    def health() -> dict:
        try:
            reference_status = verify()["status"]
        except (OSError, UnicodeError) as exc:
            reference_status = f"ERROR: {type(exc).__name__}"
        return {
            "ok": reference_status == "OK",
            "engine_version": engine_version,
            "androguard_version": package_version("androguard"),
            "reference_status": reference_status,
        }

    return app
