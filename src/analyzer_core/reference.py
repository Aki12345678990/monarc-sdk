"""Check vendored reference files against ``MANIFEST.sha256``.

The manifest is empty in Phase 1A. When it is populated, each non-blank line
is GNU ``sha256sum`` text form: 64 hex digits, two spaces, then a path
relative to the reference directory. Lines are not comments.
"""

import hashlib
from pathlib import Path

from analyzer_core.config import reference_dir

_EMPTY_MESSAGE = "No reference data vendored yet (Phase 1B)"


def verify() -> dict:
    """Return status ``EMPTY``, ``OK``, or ``MISMATCH`` with per-file results."""

    directory = reference_dir()
    text = (directory / "MANIFEST.sha256").read_text(encoding="utf-8")
    if text.strip() == "":
        return {"status": "EMPTY", "message": _EMPTY_MESSAGE, "files": []}

    files: list[dict] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if raw_line.strip() == "":
            continue
        parsed = _parse_line(raw_line)
        if parsed is None:
            files.append(
                {
                    "path": raw_line,
                    "line": line_number,
                    "expected": None,
                    "actual": None,
                    "match": False,
                }
            )
            continue
        expected, rel_path = parsed
        files.append(_check_file(directory, rel_path, expected, line_number))

    status = "OK" if files and all(item["match"] for item in files) else "MISMATCH"
    if status == "OK":
        message = "All listed reference files match their SHA256."
    else:
        message = "One or more reference files do not match."
    return {"status": status, "message": message, "files": files}


def _parse_line(line: str) -> tuple[str, str] | None:
    digest, separator, rel_path = line.partition("  ")
    if separator != "  " or len(digest) != 64 or not _is_hex(digest) or rel_path == "":
        return None
    return digest.lower(), rel_path


def _is_hex(value: str) -> bool:
    return all(char in "0123456789abcdefABCDEF" for char in value)


def _check_file(directory: Path, rel_path: str, expected: str, line_number: int) -> dict:
    record = {
        "path": rel_path,
        "line": line_number,
        "expected": expected,
        "actual": None,
        "match": False,
    }
    root = directory.resolve()
    candidate = (root / rel_path).resolve()
    if candidate != root and root not in candidate.parents:
        return record
    if not candidate.is_file():
        return record
    hasher = hashlib.sha256()
    with candidate.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    actual = hasher.hexdigest()
    record["actual"] = actual
    record["match"] = actual == expected
    return record
