"""Upload staging and report storage.

Staging files are named by job id only; the user's filename is never used on disk.
Reports are keyed by APK hash, engine version and reference manifest hash.
"""

import hashlib
import os
import re
from pathlib import Path
from typing import Protocol

from analyzer_core import __version__
from analyzer_core.config import reference_dir

REPORT_KEY_RE = re.compile(r"^[0-9a-f]{64}__[0-9A-Za-z.+\-]{1,40}__[0-9a-f]{12}$")
_JOB_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def reference_manifest_sha256() -> str:
    data = (reference_dir() / "MANIFEST.sha256").read_bytes()
    return hashlib.sha256(data).hexdigest()


def report_key(sha256: str, engine_version: str, reference_sha256: str) -> str:
    return f"{sha256}__{engine_version}__{reference_sha256[:12]}"


def current_report_key(sha256: str) -> str:
    return report_key(sha256, __version__, reference_manifest_sha256())


def is_valid_report_key(key: str) -> bool:
    return REPORT_KEY_RE.fullmatch(key) is not None


class Storage(Protocol):
    def begin_upload(self, job_id: str) -> Path: ...

    def finalize(self, job_id: str) -> Path: ...

    def open_for_analysis(self, job_id: str) -> Path: ...

    def delete_upload(self, job_id: str) -> None: ...

    def put_report(self, key: str, payload: str) -> None: ...

    def get_report(self, key: str) -> str | None: ...

    def report_exists(self, key: str) -> bool: ...


class LocalStorage:
    def __init__(self, var_dir: Path) -> None:
        self.staging_dir = Path(var_dir) / "staging"
        self.reports_dir = Path(var_dir) / "reports"
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _job_path(self, job_id: str, suffix: str) -> Path:
        if _JOB_ID_RE.fullmatch(job_id) is None:
            raise ValueError("invalid job id")
        return self.staging_dir / f"{job_id}{suffix}"

    def _report_path(self, key: str) -> Path:
        if not is_valid_report_key(key):
            raise ValueError("invalid report key")
        return self.reports_dir / f"{key}.json"

    def begin_upload(self, job_id: str) -> Path:
        """Return the ``.part`` path for a new upload; the caller creates it exclusively."""

        return self._job_path(job_id, ".part")

    def finalize(self, job_id: str) -> Path:
        part = self._job_path(job_id, ".part")
        final = self._job_path(job_id, ".apk")
        os.replace(part, final)
        return final

    def open_for_analysis(self, job_id: str) -> Path:
        return self._job_path(job_id, ".apk")

    def delete_upload(self, job_id: str) -> None:
        for suffix in (".part", ".apk"):
            self._job_path(job_id, suffix).unlink(missing_ok=True)

    def put_report(self, key: str, payload: str) -> None:
        target = self._report_path(key)
        tmp = target.with_suffix(".json.tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, target)

    def get_report(self, key: str) -> str | None:
        try:
            path = self._report_path(key)
        except ValueError:
            return None
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")

    def report_exists(self, key: str) -> bool:
        try:
            return self._report_path(key).is_file()
        except ValueError:
            return False
