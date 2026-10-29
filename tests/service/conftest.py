"""Service test fixtures. Each test gets its own temporary VAR_DIR. Archives are synthetic ZIPs."""

import io
import zipfile
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from analyzer_service.api import create_app
from analyzer_service.db import JobDB
from analyzer_service.settings import Settings
from analyzer_service.storage import LocalStorage


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    var_dir = tmp_path / "var"
    return Settings(
        var_dir=var_dir,
        db_path=var_dir / "jobs.sqlite",
        max_upload_bytes=1024 * 1024,
        job_timeout_s=900,
        lease_s=1200,
        max_attempts=2,
        upload_ttl_s=900,
        cors_origins=("http://localhost:3000",),
    )


@pytest.fixture
def make_client():
    def build(settings: Settings, **overrides) -> TestClient:
        return TestClient(create_app(replace(settings, **overrides)))

    return build


@pytest.fixture
def client(settings: Settings, make_client) -> TestClient:
    return make_client(settings)


@pytest.fixture
def storage(settings: Settings) -> LocalStorage:
    return LocalStorage(settings.var_dir)


@pytest.fixture
def db(settings: Settings) -> JobDB:
    return JobDB(settings.db_path, lease_s=settings.lease_s, max_attempts=settings.max_attempts)


@pytest.fixture
def manifest_zip():
    def build(extra: bytes = b"") -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("AndroidManifest.xml", b"<manifest/>" + extra)
            archive.writestr("classes.dex", b"dex\n035\x00")
        return buffer.getvalue()

    return build


@pytest.fixture
def staged(settings: Settings):
    def listing() -> list[Path]:
        return sorted(p for p in settings.staging_dir.iterdir() if p.is_file())

    return listing
