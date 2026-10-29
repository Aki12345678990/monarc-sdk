"""Intake checks against synthetic ZIP archives."""

import hashlib
import zipfile

import pytest

from analyzer_core.errors import AnalyzerError, ErrorCode
from analyzer_core.intake import validate


def test_non_zip(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_bytes(b"this is not a zip")
    with pytest.raises(AnalyzerError) as caught:
        validate(path)
    assert caught.value.code is ErrorCode.E_NOT_ZIP


def test_too_large(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYZER_MAX_APK_BYTES", "10")
    path = tmp_path / "oversize.bin"
    path.write_bytes(b"0123456789ABCDEF")
    with pytest.raises(AnalyzerError) as caught:
        validate(path)
    assert caught.value.code is ErrorCode.E_TOO_LARGE


def test_path_traversal(tmp_path):
    path = tmp_path / "traversal.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../evil", b"x")
    with pytest.raises(AnalyzerError) as caught:
        validate(path)
    assert caught.value.code is ErrorCode.E_PATH_TRAVERSAL


def test_zip_bomb(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYZER_MAX_COMPRESSION_RATIO", "10")
    path = tmp_path / "bomb.zip"
    payload = b"\x00" * (50 * 1024 * 1024)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("zeros.bin", payload)
    with pytest.raises(AnalyzerError) as caught:
        validate(path)
    assert caught.value.code is ErrorCode.E_ZIP_BOMB


def test_too_many_entries(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYZER_MAX_ENTRIES", "2")
    path = tmp_path / "many.zip"
    with zipfile.ZipFile(path, "w") as archive:
        for index in range(3):
            archive.writestr(f"file{index}.txt", b"x")
    with pytest.raises(AnalyzerError) as caught:
        validate(path)
    assert caught.value.code is ErrorCode.E_TOO_MANY_ENTRIES


def test_missing_manifest(tmp_path):
    path = tmp_path / "nomanifest.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("readme.txt", b"hello")
    with pytest.raises(AnalyzerError) as caught:
        validate(path)
    assert caught.value.code is ErrorCode.E_NO_MANIFEST


def test_valid_manifest_sha256(tmp_path):
    path = tmp_path / "withmanifest.zip"
    before = set(tmp_path.iterdir())
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("AndroidManifest.xml", b"<manifest />")
    result = validate(path)
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    assert result.sha256 == expected
    assert result.file_size == path.stat().st_size
    assert set(tmp_path.iterdir()) == before | {path}
