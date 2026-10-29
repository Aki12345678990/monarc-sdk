"""End-to-end smoke test against a running API and worker (no browser).

Usage (API and worker already running on 127.0.0.1:8000):
    set ANALYZER_TEST_APK=<path to one APK>   (read only)
    .venv\\Scripts\\python scripts\\e2e_smoke.py
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

BASE = os.environ.get("ANALYZER_SMOKE_BASE", "http://127.0.0.1:8000")
ROOT = Path(__file__).resolve().parents[1]
STAGING = Path(os.environ.get("ANALYZER_SVC_VAR_DIR") or ROOT / "var") / "staging"
TERMINAL = {"done", "rejected", "failed", "expired"}
FORBIDDEN = re.compile(r"score|tier|verdict|malicious|\bsafe\b|critical|high risk|low risk", re.I)
POLL_TIMEOUT_S = 900


def log(message: str) -> None:
    print(message, flush=True)


def submit(client: httpx.Client, filename: str, payload: bytes) -> tuple[str, dict, float]:
    started = time.monotonic()
    created = client.post("/api/jobs", json={"filename": filename})
    created.raise_for_status()
    job = created.json()
    uploaded = client.put(
        job["upload_url"],
        content=payload,
        headers={"Content-Type": "application/octet-stream"},
    )
    uploaded.raise_for_status()
    return job["job_id"], uploaded.json(), started


def poll(client: httpx.Client, job_id: str, started: float) -> dict:
    deadline = started + POLL_TIMEOUT_S
    last = None
    while True:
        job = client.get(f"/api/jobs/{job_id}").json()
        if job["status"] != last:
            log(f"    t+{time.monotonic() - started:7.1f}s status={job['status']}")
            last = job["status"]
        if job["status"] in TERMINAL:
            return job
        if time.monotonic() > deadline:
            raise AssertionError(f"job {job_id} not terminal after {POLL_TIMEOUT_S}s")
        time.sleep(2)


def forbidden_hits(obj, path="") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if FORBIDDEN.search(str(key)):
                hits.append(f"key {path}/{key}")
            if key == "limitations":
                continue
            hits.extend(forbidden_hits(value, f"{path}/{key}"))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            hits.extend(forbidden_hits(item, f"{path}/{index}"))
    elif isinstance(obj, str) and FORBIDDEN.search(obj):
        hits.append(f"value {path}={obj!r}")
    return hits


def main() -> int:
    apk = os.environ.get("ANALYZER_TEST_APK")
    if not apk or not Path(apk).is_file():
        log(f"ANALYZER_TEST_APK is unset or not a file: {apk!r}")
        return 2
    payload = Path(apk).read_bytes()
    log(f"APK: {Path(apk).name} ({len(payload)} bytes)")

    with httpx.Client(base_url=BASE, timeout=60) as client:
        log("a) first upload")
        job_id, after_put, started = submit(client, Path(apk).name, payload)
        log(f"    job_id={job_id} after PUT status={after_put['status']}")
        job = poll(client, job_id, started)
        elapsed_a = time.monotonic() - started
        assert job["status"] == "done", job
        report = client.get(job["report_url"])
        report.raise_for_status()
        data = report.json()
        statuses = {name: data["indicators"][name]["status"] for name in "DNAPM"}
        log(f"    done in {elapsed_a:.1f}s; report_url={job['report_url']}")
        log(f"    report status={data['status']} indicators={statuses}")
        log(f"    package={data['input']['package_name']} D={data['indicators']['D']['value']} N={data['indicators']['N']['value']}")
        assert data["status"] == "ok"
        assert statuses == {
            "D": "ok",
            "N": "ok",
            "A": "unavailable",
            "P": "not_implemented",
            "M": "not_implemented",
        }, statuses
        hits = forbidden_hits(data)
        assert hits == [], hits
        log("    no forbidden keys/values")

        log("b) same APK again (cache)")
        job_id_b, after_put_b, started_b = submit(client, Path(apk).name, payload)
        job_b = poll(client, job_id_b, started_b)
        elapsed_b = time.monotonic() - started_b
        log(f"    job_id={job_id_b} after PUT status={after_put_b['status']} done in {elapsed_b:.2f}s")
        assert after_put_b["status"] == "done", "cache hit must finish at upload without queuing"
        assert job_b["status"] == "done"
        assert job_b["report_url"] == job["report_url"]
        assert elapsed_b < 5, elapsed_b

        log("c) non-zip upload")
        job_id_c, after_put_c, started_c = submit(client, "not-an-apk.apk", b"this is not a zip archive\n" * 4)
        job_c = poll(client, job_id_c, started_c)
        log(f"    job_id={job_id_c} status={job_c['status']} error_code={job_c['error_code']}")
        assert job_c["status"] == "rejected"
        assert job_c["error_code"] == "E_NOT_ZIP"

        log("d) staging directory")
        leftovers = sorted(p.name for p in STAGING.iterdir()) if STAGING.exists() else []
        log(f"    {STAGING}: {leftovers}")
        assert leftovers == []

        log("e) health")
        health = client.get("/api/health").json()
        log("    " + json.dumps(health))

    log(f"FIRST_JOB_ID={job_id}")
    log("E2E SMOKE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
