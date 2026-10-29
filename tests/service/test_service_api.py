"""Job API: create, upload, intake, cache, reports, health."""

import hashlib

from analyzer_core.report import Report, ReportInput
from analyzer_service.storage import current_report_key

OCTET = {"Content-Type": "application/octet-stream"}


def _create(client, filename="sample.apk"):
    response = client.post("/api/jobs", json={"filename": filename})
    assert response.status_code == 200
    return response.json()


def test_create_job_is_awaiting_upload(client, settings):
    created = _create(client)
    assert created["upload_url"] == f"/api/jobs/{created['job_id']}/upload"
    assert created["upload_method"] == "PUT"
    assert created["max_bytes"] == settings.max_upload_bytes
    assert created["expires_at"].endswith("Z")
    job = client.get(f"/api/jobs/{created['job_id']}").json()
    assert job["status"] == "awaiting_upload"
    assert job["report_url"] is None


def test_security_headers_present(client):
    response = client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_cors_limited_to_configured_origin(client):
    allowed = client.options(
        "/api/jobs",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"
    denied = client.options(
        "/api/jobs",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert denied.headers.get("access-control-allow-origin") is None


def test_filename_is_display_only_and_sanitised(client, db):
    created = _create(client, "..\\..\\" + "a" * 300 + "\x00.apk")
    job = db.get_job(created["job_id"])
    assert "\\" not in job.original_filename and "/" not in job.original_filename
    assert "\x00" not in job.original_filename
    assert len(job.original_filename) <= 200


def test_upload_non_zip_is_rejected_and_staging_empty(client, staged):
    created = _create(client)
    response = client.put(created["upload_url"], content=b"this is not a zip file", headers=OCTET)
    assert response.status_code == 200
    job = client.get(f"/api/jobs/{created['job_id']}").json()
    assert job["status"] == "rejected"
    assert job["error_code"] == "E_NOT_ZIP"
    assert staged() == []


def test_upload_over_limit_declared_length_is_413(client, settings, staged, make_client):
    small = make_client(settings, max_upload_bytes=1000)
    created = _create(small)
    response = small.put(created["upload_url"], content=b"x" * 5000, headers=OCTET)
    assert response.status_code == 413
    assert staged() == []
    job = small.get(f"/api/jobs/{created['job_id']}").json()
    assert job["status"] == "rejected"
    assert job["error_code"] == "E_TOO_LARGE"


def test_upload_over_limit_streamed_is_413_and_no_part_left(settings, staged, make_client):
    small = make_client(settings, max_upload_bytes=1000)
    created = _create(small)

    def body():
        for _ in range(10):
            yield b"x" * 600

    response = small.put(created["upload_url"], content=body(), headers=OCTET)
    assert response.status_code == 413
    assert staged() == []
    assert not list(settings.staging_dir.glob("*.part"))


def test_upload_to_expired_job_is_410(settings, make_client, staged):
    expired = make_client(settings, upload_ttl_s=-1)
    created = _create(expired)
    response = expired.put(created["upload_url"], content=b"PK\x03\x04", headers=OCTET)
    assert response.status_code == 410
    assert expired.get(f"/api/jobs/{created['job_id']}").json()["status"] == "expired"
    assert staged() == []


def test_second_upload_to_same_job_is_409(client):
    created = _create(client)
    first = client.put(created["upload_url"], content=b"not a zip", headers=OCTET)
    assert first.status_code == 200
    second = client.put(created["upload_url"], content=b"not a zip", headers=OCTET)
    assert second.status_code == 409


def test_unknown_job_is_404(client):
    assert client.get("/api/jobs/00000000-0000-4000-8000-000000000000").status_code == 404
    assert client.get("/api/jobs/not-a-uuid").status_code == 404


def test_report_key_traversal_never_reads_outside_reports(client, settings):
    secret = settings.var_dir / "secret.json"
    secret.write_text('{"secret": true}', encoding="utf-8")
    for attempt in (
        "..%2F..%2Fx",
        "..%2Fsecret",
        "..%5Csecret",
        "..%2F..%2F..%2Fpyproject.toml",
        "%2e%2e%2fsecret",
        "a" * 64 + "__0.1.0a2__" + "b" * 12 + "%2F..%2F..%2Fsecret",
    ):
        response = client.get(f"/api/reports/{attempt}")
        assert response.status_code in (400, 404), attempt
        assert b"secret" not in response.content


def test_missing_report_is_404(client):
    key = "a" * 64 + "__0.1.0a2__" + "b" * 12
    assert client.get(f"/api/reports/{key}").status_code == 404


def test_cache_hit_marks_done_without_queuing(client, storage, staged, db, manifest_zip):
    payload = manifest_zip()
    sha256 = hashlib.sha256(payload).hexdigest()
    key = current_report_key(sha256)
    seeded = Report(status="ok", input=ReportInput(sha256=sha256, file_size=len(payload)))
    storage.put_report(key, seeded.to_json())

    created = _create(client)
    response = client.put(created["upload_url"], content=payload, headers=OCTET)
    assert response.status_code == 200
    job = client.get(f"/api/jobs/{created['job_id']}").json()
    assert job["status"] == "done"
    assert job["sha256"] == sha256
    assert job["report_url"] == f"/api/reports/{key}"
    assert staged() == []
    assert db.lease_next_job().job is None
    report = client.get(job["report_url"])
    assert report.status_code == 200
    assert report.json()["input"]["sha256"] == sha256


def test_valid_upload_without_cache_is_queued(client, staged, manifest_zip):
    payload = manifest_zip(b"queued")
    created = _create(client)
    response = client.put(created["upload_url"], content=payload, headers=OCTET)
    assert response.status_code == 200
    job = client.get(f"/api/jobs/{created['job_id']}").json()
    assert job["status"] == "queued"
    assert job["file_size"] == len(payload)
    assert [p.name for p in staged()] == [f"{created['job_id']}.apk"]


def test_error_report_is_not_a_cache_hit(client, storage, manifest_zip):
    payload = manifest_zip(b"error-cached")
    sha256 = hashlib.sha256(payload).hexdigest()
    storage.put_report(
        current_report_key(sha256),
        Report(status="error", input=ReportInput(sha256=sha256)).to_json(),
    )
    created = _create(client)
    client.put(created["upload_url"], content=payload, headers=OCTET)
    assert client.get(f"/api/jobs/{created['job_id']}").json()["status"] == "queued"


def test_expired_awaiting_jobs_are_cleaned_up(settings, make_client, db, storage):
    expired_client = make_client(settings, upload_ttl_s=-1)
    created = _create(expired_client)
    part = storage.begin_upload(created["job_id"])
    part.write_bytes(b"partial")
    fresh = make_client(settings)
    fresh.get("/api/health")
    assert db.get_job(created["job_id"]).status == "expired"
    assert not part.exists()


def test_health(client):
    body = client.get("/api/health").json()
    assert set(body) == {"ok", "engine_version", "androguard_version", "reference_status"}
    assert body["engine_version"] == "0.1.0a2"
    assert body["androguard_version"] == "3.3.5"
