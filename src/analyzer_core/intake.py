"""Validate an APK candidate without extracting it."""

import hashlib
import os
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

from analyzer_core.config import (
    max_apk_bytes,
    max_compression_ratio,
    max_entries,
    max_uncompressed_bytes,
)
from analyzer_core.errors import AnalyzerError, ErrorCode

_CHUNK_BYTES = 1024 * 1024
_ZIP_MAGIC = b"PK\x03\x04"
_DRIVE_LETTER = re.compile(r"^[A-Za-z]:")


@dataclass(frozen=True)
class IntakeResult:
    sha256: str
    file_size: int


def validate(path: str | os.PathLike[str]) -> IntakeResult:
    """Hash ``path`` and reject archives that fail the intake checks.

    Rejection order is fixed: missing file, size, ZIP magic, bad ZIP,
    entry count, path traversal, uncompressed size, compression ratio,
    missing ``AndroidManifest.xml``. The central directory is read.
    Nothing is extracted.
    """

    candidate = Path(path)
    if not candidate.is_file():
        raise AnalyzerError(ErrorCode.E_NOT_FOUND, "File does not exist.")

    file_size = candidate.stat().st_size
    if file_size > max_apk_bytes():
        raise AnalyzerError(
            ErrorCode.E_TOO_LARGE,
            "File exceeds MAX_APK_BYTES.",
            file_size=file_size,
        )

    sha256, magic_ok = _hash_file(candidate)
    if not magic_ok:
        raise AnalyzerError(
            ErrorCode.E_NOT_ZIP,
            "File does not start with a ZIP local file header.",
            sha256=sha256,
            file_size=file_size,
        )

    try:
        archive = zipfile.ZipFile(candidate)
    except zipfile.BadZipFile as exc:
        raise AnalyzerError(
            ErrorCode.E_NOT_ZIP,
            "ZIP central directory could not be read.",
            sha256=sha256,
            file_size=file_size,
        ) from exc

    with archive:
        entries = archive.infolist()
        if len(entries) > max_entries():
            raise AnalyzerError(
                ErrorCode.E_TOO_MANY_ENTRIES,
                "ZIP entry count exceeds MAX_ENTRIES.",
                sha256=sha256,
                file_size=file_size,
            )
        for entry in entries:
            if _entry_name_rejected(entry.filename):
                raise AnalyzerError(
                    ErrorCode.E_PATH_TRAVERSAL,
                    "ZIP entry name is absolute or contains a parent-directory segment.",
                    sha256=sha256,
                    file_size=file_size,
                )

        uncompressed = sum(entry.file_size for entry in entries)
        if uncompressed > max_uncompressed_bytes():
            raise AnalyzerError(
                ErrorCode.E_ZIP_BOMB,
                "Declared uncompressed size exceeds MAX_UNCOMPRESSED_BYTES.",
                sha256=sha256,
                file_size=file_size,
            )

        ratio_limit = max_compression_ratio()
        for entry in entries:
            if entry.compress_size > 0 and (entry.file_size / entry.compress_size) > ratio_limit:
                raise AnalyzerError(
                    ErrorCode.E_ZIP_BOMB,
                    "ZIP entry compression ratio exceeds MAX_COMPRESSION_RATIO.",
                    sha256=sha256,
                    file_size=file_size,
                )

        if not any(entry.filename == "AndroidManifest.xml" for entry in entries):
            raise AnalyzerError(
                ErrorCode.E_NO_MANIFEST,
                "ZIP archive has no AndroidManifest.xml entry.",
                sha256=sha256,
                file_size=file_size,
            )

    return IntakeResult(sha256=sha256, file_size=file_size)


def _hash_file(path: Path) -> tuple[str, bool]:
    hasher = hashlib.sha256()
    magic_ok = False
    started = False
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(_CHUNK_BYTES)
            if not chunk:
                break
            if not started:
                magic_ok = chunk[:4] == _ZIP_MAGIC
                started = True
            hasher.update(chunk)
    return hasher.hexdigest(), magic_ok


def _entry_name_rejected(name: str) -> bool:
    if name.startswith("/") or name.startswith("\\"):
        return True
    if os.path.isabs(name):
        return True
    if _DRIVE_LETTER.match(name):
        return True
    parts = re.split(r"[/\\]", name)
    return ".." in parts
