"""CLI exit codes and report files. Archives are synthetic ZIPs."""

import hashlib
import json
import os
import subprocess
import sys
import zipfile


def test_analyze_missing_manifest_exits_2(tmp_path):
    apk_path = tmp_path / "nomanifest.zip"
    with zipfile.ZipFile(apk_path, "w") as archive:
        archive.writestr("readme.txt", b"hello")
    out_dir = tmp_path / "out"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "analyzer_core",
            "analyze",
            str(apk_path),
            "--out",
            str(out_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    digest = hashlib.sha256(apk_path.read_bytes()).hexdigest()
    written = json.loads((out_dir / f"{digest}.json").read_text(encoding="utf-8"))
    assert written["status"] == "error"
    assert written["errors"][0]["code"] == "E_NO_MANIFEST"
    markdown = (out_dir / f"{digest}.md").read_text(encoding="utf-8")
    assert "E_NO_MANIFEST" in markdown
    assert "status: error" in markdown


def test_verify_reference_empty():
    completed = subprocess.run(
        [sys.executable, "-m", "analyzer_core", "verify-reference"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert completed.stdout.strip() == "EMPTY: No reference data vendored yet (Phase 1B)"


def test_verify_reference_wrong_hash_exits_4(tmp_path):
    payload = tmp_path / "blob.bin"
    payload.write_bytes(b"hello")
    (tmp_path / "MANIFEST.sha256").write_text(f"{'0' * 64}  blob.bin\n", encoding="utf-8")
    completed = _verify_reference(tmp_path)
    assert completed.returncode == 4
    assert "MISMATCH" in completed.stdout


def test_verify_reference_correct_hash_exits_0(tmp_path):
    payload = tmp_path / "blob.bin"
    payload.write_bytes(b"hello")
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    (tmp_path / "MANIFEST.sha256").write_text(f"{digest}  blob.bin\n", encoding="utf-8")
    completed = _verify_reference(tmp_path)
    assert completed.returncode == 0
    assert "OK" in completed.stdout


def _verify_reference(reference_dir):
    env = os.environ.copy()
    env["ANALYZER_REFERENCE_DIR"] = str(reference_dir)
    return subprocess.run(
        [sys.executable, "-m", "analyzer_core", "verify-reference"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_version_prints_androguard_pin():
    completed = subprocess.run(
        [sys.executable, "-m", "analyzer_core", "version"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "3.3.5" in completed.stdout
    assert "0.1.0a1" in completed.stdout
