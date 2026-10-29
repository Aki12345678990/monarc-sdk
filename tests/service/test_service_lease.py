"""Lease queue semantics."""

import time

from analyzer_service.db import JobDB


def _queued(db: JobDB, now: float) -> str:
    job = db.create_job("a.apk", 900, now=now)
    assert db.mark_uploaded(job.id, sha256="0" * 64, file_size=1, cached_report_key=None)
    return job.id


def test_queued_job_is_leased_once(db):
    now = time.time()
    job_id = _queued(db, now)
    first = db.lease_next_job(now=now)
    assert first.job is not None and first.job.id == job_id
    assert first.job.status == "running"
    assert first.job.attempts == 1
    assert first.job.leased_until == now + db.lease_s
    assert db.lease_next_job(now=now + 1).job is None


def test_oldest_queued_job_first(db):
    now = time.time()
    older = _queued(db, now - 10)
    _queued(db, now)
    assert db.lease_next_job(now=now).job.id == older


def test_expired_lease_is_re_leased(db):
    now = time.time()
    job_id = _queued(db, now)
    db.lease_next_job(now=now)
    later = now + db.lease_s + 1
    again = db.lease_next_job(now=later)
    assert again.job is not None and again.job.id == job_id
    assert again.job.attempts == 2
    assert again.job.leased_until == later + db.lease_s


def test_attempts_exhausted_becomes_failed(db):
    now = time.time()
    job_id = _queued(db, now)
    db.lease_next_job(now=now)
    t2 = now + db.lease_s + 1
    db.lease_next_job(now=t2)
    t3 = t2 + db.lease_s + 1
    result = db.lease_next_job(now=t3)
    assert result.job is None
    assert result.exhausted_ids == [job_id]
    job = db.get_job(job_id)
    assert job.status == "failed"
    assert job.error_code == "E_LEASE_EXHAUSTED"
    assert job.attempts == db.max_attempts


def test_awaiting_upload_is_never_leased(db):
    db.create_job("a.apk", 900)
    assert db.lease_next_job().job is None


def test_wal_mode(db):
    import sqlite3

    conn = sqlite3.connect(db.path)
    try:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    finally:
        conn.close()
