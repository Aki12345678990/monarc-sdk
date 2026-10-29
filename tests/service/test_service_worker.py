"""Worker outcomes and staging cleanup. analyze() is replaced by fakes; no APK is parsed."""

from analyzer_core.report import Report, ReportError, ReportInput
from analyzer_service.storage import current_report_key
from analyzer_service.worker import run_once

SHA = "c" * 64


def _queued_with_file(db, storage) -> str:
    job = db.create_job("a.apk", 900)
    storage.open_for_analysis(job.id).write_bytes(b"PK\x03\x04synthetic")
    assert db.mark_uploaded(job.id, sha256=SHA, file_size=13, cached_report_key=None)
    return job.id


def _boom(_path):
    raise RuntimeError("simulated failure")


def test_exception_requeues_then_fails_and_staging_is_deleted(db, storage, staged):
    job_id = _queued_with_file(db, storage)

    assert run_once(db, storage, _boom) == "queued"
    assert db.get_job(job_id).status == "queued"
    assert storage.open_for_analysis(job_id).exists()

    assert run_once(db, storage, _boom) == "failed"
    job = db.get_job(job_id)
    assert job.status == "failed"
    assert job.error_code == "E_INTERNAL"
    assert "simulated failure" in job.error_message
    assert staged() == []


def test_ok_report_is_stored_and_job_done(db, storage, staged):
    job_id = _queued_with_file(db, storage)

    def fake(_path):
        return Report(status="ok", input=ReportInput(sha256=SHA, file_size=13))

    assert run_once(db, storage, fake) == "done"
    job = db.get_job(job_id)
    assert job.status == "done"
    assert job.report_key == current_report_key(SHA)
    assert storage.report_exists(job.report_key)
    assert staged() == []


def test_error_report_fails_job_but_is_stored(db, storage, staged):
    job_id = _queued_with_file(db, storage)

    def fake(_path):
        return Report(
            status="error",
            errors=[ReportError(code="E_TIMEOUT", message="Isolated call exceeded 900 seconds.")],
            input=ReportInput(sha256=SHA, file_size=13),
        )

    assert run_once(db, storage, fake) == "failed"
    job = db.get_job(job_id)
    assert job.status == "failed"
    assert job.error_code == "E_TIMEOUT"
    assert storage.report_exists(current_report_key(SHA))
    assert job.report_key == current_report_key(SHA)
    assert staged() == []


def test_idle_returns_none(db, storage):
    assert run_once(db, storage, _boom) is None
