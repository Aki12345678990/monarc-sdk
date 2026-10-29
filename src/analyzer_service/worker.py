"""Single-job worker: lease a job, run analyzer_core.pipeline.analyze(), store the report."""

import logging
import os
import threading
import time
from collections.abc import Callable

from analyzer_core.errors import ErrorCode
from analyzer_core.pipeline import analyze
from analyzer_core.report import Report
from analyzer_service.db import Job, JobDB
from analyzer_service.settings import Settings, load_settings
from analyzer_service.storage import LocalStorage, Storage, current_report_key

log = logging.getLogger("analyzer_service.worker")

IDLE_SLEEP_S = 2.0

AnalyzeFn = Callable[[os.PathLike[str] | str], Report]


def process_job(job: Job, db: JobDB, storage: Storage, analyze_fn: AnalyzeFn = analyze) -> str:
    """Run one leased job to a terminal state or requeue it; return the resulting status."""

    terminal = False
    try:
        report = analyze_fn(storage.open_for_analysis(job.id))
        sha256 = report.input.sha256 or job.sha256
        key = current_report_key(sha256) if sha256 else None
        if key is not None:
            storage.put_report(key, report.to_json())
        if report.status == "ok" and key is not None:
            db.complete(job.id, key)
            terminal = True
            return "done"
        error = report.errors[0] if report.errors else None
        db.fail(
            job.id,
            error.code if error else ErrorCode.E_INTERNAL.value,
            error.message if error else "Report has status error and no error entry.",
            key,
        )
        terminal = True
        return "failed"
    except Exception as exc:
        log.exception("job %s raised", job.id)
        if job.attempts < db.max_attempts:
            db.requeue(job.id)
            return "queued"
        db.fail(job.id, ErrorCode.E_INTERNAL.value, f"{type(exc).__name__}: {exc}")
        terminal = True
        return "failed"
    finally:
        if terminal:
            storage.delete_upload(job.id)


def run_once(db: JobDB, storage: Storage, analyze_fn: AnalyzeFn = analyze) -> str | None:
    """Lease and process at most one job. Returns the job's resulting status, or None if idle."""

    lease = db.lease_next_job()
    for job_id in lease.exhausted_ids:
        storage.delete_upload(job_id)
    if lease.job is None:
        return None
    log.info("leased job %s (attempt %d)", lease.job.id, lease.job.attempts)
    started = time.monotonic()
    status = process_job(lease.job, db, storage, analyze_fn)
    log.info("job %s -> %s in %.1fs", lease.job.id, status, time.monotonic() - started)
    return status


def run_forever(settings: Settings | None = None, stop: threading.Event | None = None) -> None:
    settings = settings or load_settings()
    os.environ["ANALYZER_PARSE_TIMEOUT_S"] = str(settings.job_timeout_s)
    storage = LocalStorage(settings.var_dir)
    db = JobDB(settings.db_path, lease_s=settings.lease_s, max_attempts=settings.max_attempts)
    stop = stop or threading.Event()
    log.info("worker started; db=%s timeout=%ss", settings.db_path, settings.job_timeout_s)
    while not stop.is_set():
        if run_once(db, storage) is None:
            stop.wait(IDLE_SLEEP_S)
