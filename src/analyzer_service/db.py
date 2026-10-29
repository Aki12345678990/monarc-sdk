"""SQLite job table and lease queue.

Timestamps are stored as UTC epoch seconds (REAL) and rendered as ISO 8601 by the API.
"""

import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

AWAITING_UPLOAD = "awaiting_upload"
QUEUED = "queued"
RUNNING = "running"
DONE = "done"
REJECTED = "rejected"
FAILED = "failed"
EXPIRED = "expired"

STATUSES = (AWAITING_UPLOAD, QUEUED, RUNNING, DONE, REJECTED, FAILED, EXPIRED)
TERMINAL_STATUSES = (DONE, REJECTED, FAILED, EXPIRED)

E_LEASE_EXHAUSTED = "E_LEASE_EXHAUSTED"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN (
        'awaiting_upload', 'queued', 'running', 'done', 'rejected', 'failed', 'expired'
    )),
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    upload_expires_at REAL NOT NULL,
    original_filename TEXT,
    file_size INTEGER,
    sha256 TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    leased_until REAL,
    error_code TEXT,
    error_message TEXT,
    report_key TEXT
);
CREATE INDEX IF NOT EXISTS jobs_status_created ON jobs (status, created_at);
"""

_COLUMNS = (
    "id, status, created_at, updated_at, upload_expires_at, original_filename, file_size, "
    "sha256, attempts, leased_until, error_code, error_message, report_key"
)


@dataclass(frozen=True)
class Job:
    id: str
    status: str
    created_at: float
    updated_at: float
    upload_expires_at: float
    original_filename: str | None
    file_size: int | None
    sha256: str | None
    attempts: int
    leased_until: float | None
    error_code: str | None
    error_message: str | None
    report_key: str | None


@dataclass(frozen=True)
class LeaseResult:
    job: Job | None
    exhausted_ids: list[str] = field(default_factory=list)


def sanitize_filename(name: str) -> str:
    """Display-only filename: last path segment, printable characters, at most 200 chars."""

    base = name.replace("\\", "/").rsplit("/", 1)[-1]
    cleaned = "".join(ch for ch in base if ch.isprintable()).strip()
    return cleaned[:200]


class JobDB:
    def __init__(self, path: Path, *, lease_s: int, max_attempts: int) -> None:
        self.path = Path(path)
        self.lease_s = lease_s
        self.max_attempts = max_attempts
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(_SCHEMA)

    def _connect(self) -> "_Closing":
        conn = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return _Closing(conn)

    @staticmethod
    def _job(row: sqlite3.Row | None) -> Job | None:
        if row is None:
            return None
        return Job(**{key: row[key] for key in row.keys()})

    def create_job(self, filename: str, upload_ttl_s: int, now: float | None = None) -> Job:
        now = time.time() if now is None else now
        job_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO jobs (id, status, created_at, updated_at, upload_expires_at, "
                "original_filename, attempts) VALUES (?, ?, ?, ?, ?, ?, 0)",
                (job_id, AWAITING_UPLOAD, now, now, now + upload_ttl_s, sanitize_filename(filename)),
            )
        job = self.get_job(job_id)
        assert job is not None
        return job

    def get_job(self, job_id: str) -> Job | None:
        with self._connect() as conn:
            row = conn.execute(f"SELECT {_COLUMNS} FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._job(row)

    def _update(self, job_id: str, expected: tuple[str, ...], **fields: object) -> bool:
        fields["updated_at"] = time.time()
        assignments = ", ".join(f"{key} = ?" for key in fields)
        placeholders = ", ".join("?" for _ in expected)
        with self._connect() as conn:
            cur = conn.execute(
                f"UPDATE jobs SET {assignments} WHERE id = ? AND status IN ({placeholders})",
                (*fields.values(), job_id, *expected),
            )
        return cur.rowcount == 1

    def mark_expired(self, job_id: str) -> bool:
        return self._update(job_id, (AWAITING_UPLOAD,), status=EXPIRED)

    def mark_rejected(
        self,
        job_id: str,
        error_code: str,
        error_message: str,
        *,
        sha256: str | None = None,
        file_size: int | None = None,
    ) -> bool:
        return self._update(
            job_id,
            (AWAITING_UPLOAD,),
            status=REJECTED,
            error_code=error_code,
            error_message=error_message,
            sha256=sha256,
            file_size=file_size,
        )

    def mark_uploaded(
        self,
        job_id: str,
        *,
        sha256: str,
        file_size: int,
        cached_report_key: str | None,
    ) -> bool:
        if cached_report_key is not None:
            return self._update(
                job_id,
                (AWAITING_UPLOAD,),
                status=DONE,
                sha256=sha256,
                file_size=file_size,
                report_key=cached_report_key,
            )
        return self._update(
            job_id, (AWAITING_UPLOAD,), status=QUEUED, sha256=sha256, file_size=file_size
        )

    def mark_upload_failed(self, job_id: str, error_code: str, error_message: str) -> bool:
        return self._update(
            job_id,
            (AWAITING_UPLOAD,),
            status=FAILED,
            error_code=error_code,
            error_message=error_message,
        )

    def complete(self, job_id: str, report_key: str) -> bool:
        return self._update(job_id, (RUNNING,), status=DONE, report_key=report_key, leased_until=None)

    def fail(
        self,
        job_id: str,
        error_code: str,
        error_message: str,
        report_key: str | None = None,
    ) -> bool:
        return self._update(
            job_id,
            (RUNNING,),
            status=FAILED,
            error_code=error_code,
            error_message=error_message,
            report_key=report_key,
            leased_until=None,
        )

    def requeue(self, job_id: str) -> bool:
        return self._update(job_id, (RUNNING,), status=QUEUED, leased_until=None)

    def expire_uploads(self, now: float | None = None, exclude: set[str] | None = None) -> list[str]:
        """Mark awaiting_upload jobs past their upload deadline as expired; return their ids."""

        now = time.time() if now is None else now
        exclude = exclude or set()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                rows = conn.execute(
                    "SELECT id FROM jobs WHERE status = ? AND upload_expires_at < ?",
                    (AWAITING_UPLOAD, now),
                ).fetchall()
                ids = [row["id"] for row in rows if row["id"] not in exclude]
                for job_id in ids:
                    conn.execute(
                        "UPDATE jobs SET status = ?, updated_at = ? WHERE id = ? AND status = ?",
                        (EXPIRED, now, job_id, AWAITING_UPLOAD),
                    )
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
        return ids

    def lease_next_job(self, now: float | None = None) -> LeaseResult:
        """Lease the oldest runnable job inside one BEGIN IMMEDIATE transaction.

        Runnable: queued, or running with an expired lease and attempts left.
        Running jobs whose lease expired with no attempts left become failed
        with E_LEASE_EXHAUSTED; their ids are returned so staging can be cleaned.
        """

        now = time.time() if now is None else now
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                exhausted = [
                    row["id"]
                    for row in conn.execute(
                        "SELECT id FROM jobs WHERE status = ? AND leased_until < ? AND attempts >= ?",
                        (RUNNING, now, self.max_attempts),
                    ).fetchall()
                ]
                for job_id in exhausted:
                    conn.execute(
                        "UPDATE jobs SET status = ?, error_code = ?, error_message = ?, "
                        "leased_until = NULL, updated_at = ? WHERE id = ?",
                        (
                            FAILED,
                            E_LEASE_EXHAUSTED,
                            "Lease expired with no attempts left.",
                            now,
                            job_id,
                        ),
                    )
                row = conn.execute(
                    f"SELECT {_COLUMNS} FROM jobs "
                    "WHERE status = ? OR (status = ? AND leased_until < ? AND attempts < ?) "
                    "ORDER BY created_at, rowid LIMIT 1",
                    (QUEUED, RUNNING, now, self.max_attempts),
                ).fetchone()
                leased: Job | None = None
                if row is not None:
                    conn.execute(
                        "UPDATE jobs SET status = ?, leased_until = ?, attempts = attempts + 1, "
                        "updated_at = ? WHERE id = ?",
                        (RUNNING, now + self.lease_s, now, row["id"]),
                    )
                    leased = self._job(
                        conn.execute(f"SELECT {_COLUMNS} FROM jobs WHERE id = ?", (row["id"],)).fetchone()
                    )
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
        return LeaseResult(job=leased, exhausted_ids=exhausted)


class _Closing:
    """Context manager that closes the connection on exit (sqlite3's own only ends transactions)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def __enter__(self) -> sqlite3.Connection:
        return self._conn

    def __exit__(self, *exc: object) -> None:
        self._conn.close()
