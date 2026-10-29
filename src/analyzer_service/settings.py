"""Service settings. Each value can be overridden by an ``ANALYZER_SVC_`` environment variable."""

import os
from dataclasses import dataclass
from pathlib import Path

from analyzer_core.config import max_apk_bytes

ROOT = Path(__file__).resolve().parents[2]
_PREFIX = "ANALYZER_SVC_"


@dataclass(frozen=True)
class Settings:
    var_dir: Path
    db_path: Path
    max_upload_bytes: int
    job_timeout_s: int
    lease_s: int
    max_attempts: int
    upload_ttl_s: int
    cors_origins: tuple[str, ...]

    @property
    def staging_dir(self) -> Path:
        return self.var_dir / "staging"

    @property
    def reports_dir(self) -> Path:
        return self.var_dir / "reports"


def _env(name: str) -> str | None:
    raw = os.environ.get(_PREFIX + name)
    if raw is None or raw.strip() == "":
        return None
    return raw.strip()


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    return default if raw is None else int(raw)


def load_settings() -> Settings:
    """Read settings from the environment at call time."""

    var_dir = Path(_env("VAR_DIR") or ROOT / "var")
    db_path = Path(_env("DB_PATH") or var_dir / "jobs.sqlite")
    origins_raw = _env("CORS_ORIGINS")
    origins = (
        tuple(item.strip() for item in origins_raw.split(",") if item.strip())
        if origins_raw
        else ("http://localhost:3000",)
    )
    return Settings(
        var_dir=var_dir,
        db_path=db_path,
        max_upload_bytes=_env_int("MAX_UPLOAD_BYTES", max_apk_bytes()),
        job_timeout_s=_env_int("JOB_TIMEOUT_S", 900),
        lease_s=_env_int("LEASE_S", 1200),
        max_attempts=_env_int("MAX_ATTEMPTS", 2),
        upload_ttl_s=_env_int("UPLOAD_TTL_S", 900),
        cors_origins=origins,
    )
