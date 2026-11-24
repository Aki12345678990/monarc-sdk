"""Access code, unhealthy reference, and the serve command."""

import uvicorn

from analyzer_service.__main__ import main
from analyzer_service.worker import run_worker_process


def test_create_job_rejects_missing_and_wrong_access_code(settings, make_client):
    client = make_client(settings, access_code="correct-code")
    missing = client.post("/api/jobs", json={"filename": "sample.apk"})
    assert missing.status_code == 401
    assert missing.json() == {"detail": "Access code required."}
    wrong = client.post(
        "/api/jobs",
        json={"filename": "sample.apk"},
        headers={"X-Access-Code": "nope"},
    )
    assert wrong.status_code == 401
    assert wrong.json() == {"detail": "Access code required."}


def test_create_job_accepts_the_correct_access_code(settings, make_client):
    client = make_client(settings, access_code="correct-code")
    response = client.post(
        "/api/jobs",
        json={"filename": "sample.apk"},
        headers={"X-Access-Code": "correct-code"},
    )
    assert response.status_code == 200
    assert response.json()["upload_method"] == "PUT"


def test_create_job_is_open_when_access_code_is_unset(client):
    response = client.post("/api/jobs", json={"filename": "sample.apk"})
    assert response.status_code == 200


def test_health_is_503_when_reference_mismatches(client, monkeypatch):
    monkeypatch.setattr("analyzer_service.api.verify", lambda: {"status": "MISMATCH"})
    response = client.get("/api/health")
    assert response.status_code == 503
    body = response.json()
    assert body["ok"] is False
    assert body["reference_status"] == "MISMATCH"
    assert set(body) == {"ok", "engine_version", "androguard_version", "reference_status"}


def test_serve_wires_host_port_and_single_worker(monkeypatch, tmp_path):
    monkeypatch.setenv("ANALYZER_SVC_VAR_DIR", str(tmp_path / "var"))
    monkeypatch.setenv("ANALYZER_SVC_HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "8123")

    captured: dict = {}

    def fake_run(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

    class FakeProcess:
        def __init__(self, *args, **kwargs):
            captured["target"] = kwargs.get("target")
            self.exitcode = None

        def start(self):
            captured["started"] = True

        def is_alive(self):
            return True

        def terminate(self):
            captured["terminated"] = True

        def join(self, timeout=None):
            return None

    class FakeContext:
        def Process(self, *args, **kwargs):
            return FakeProcess(*args, **kwargs)

    def get_context(method):
        captured["start_method"] = method
        return FakeContext()

    monkeypatch.setattr(uvicorn, "run", fake_run)
    monkeypatch.setattr("analyzer_service.__main__.multiprocessing.get_context", get_context)

    assert main(["serve"]) == 0
    assert captured["started"] is True
    assert captured["start_method"] == "spawn"
    assert captured["target"] is run_worker_process
    assert captured["kwargs"]["host"] == "0.0.0.0"
    assert captured["kwargs"]["port"] == 8123
    assert captured["kwargs"]["workers"] == 1
    assert captured["kwargs"]["proxy_headers"] is True
    assert captured["kwargs"]["forwarded_allow_ips"] == "*"
