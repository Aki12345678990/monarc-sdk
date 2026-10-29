"""Runtime limits for intake and isolated parsing.

Defaults are overridden by environment variables prefixed with ``ANALYZER_``.
Each lookup reads the environment at call time.
"""

import os
from pathlib import Path

# Byte caps use 1024-based units: 300 MB = 300 * 1024 * 1024, 2 GB = 2 * 1024**3.
MAX_APK_BYTES = 300 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
MAX_ENTRIES = 100000
MAX_COMPRESSION_RATIO = 200
PARSE_TIMEOUT_S = 300


def _from_env(name: str, default: int) -> int:
    raw = os.environ.get(f"ANALYZER_{name}")
    if raw is None or raw == "":
        return default
    return int(raw)


def max_apk_bytes() -> int:
    return _from_env("MAX_APK_BYTES", MAX_APK_BYTES)


def max_uncompressed_bytes() -> int:
    return _from_env("MAX_UNCOMPRESSED_BYTES", MAX_UNCOMPRESSED_BYTES)


def max_entries() -> int:
    return _from_env("MAX_ENTRIES", MAX_ENTRIES)


def max_compression_ratio() -> int:
    return _from_env("MAX_COMPRESSION_RATIO", MAX_COMPRESSION_RATIO)


def parse_timeout_s() -> int:
    return _from_env("PARSE_TIMEOUT_S", PARSE_TIMEOUT_S)


def reference_dir() -> Path:
    """Directory that contains ``MANIFEST.sha256``.

    ``ANALYZER_REFERENCE_DIR`` overrides it. The default is ``data/reference``
    under the repository root.
    """

    raw = os.environ.get("ANALYZER_REFERENCE_DIR")
    if raw is None or raw == "":
        return Path(__file__).resolve().parents[2] / "data" / "reference"
    return Path(raw)
