"""Error codes and the exception raised by intake, isolation, and the pipeline."""

from enum import Enum


class ErrorCode(Enum):
    E_NOT_FOUND = "E_NOT_FOUND"
    E_NOT_ZIP = "E_NOT_ZIP"
    E_TOO_LARGE = "E_TOO_LARGE"
    E_ZIP_BOMB = "E_ZIP_BOMB"
    E_TOO_MANY_ENTRIES = "E_TOO_MANY_ENTRIES"
    E_PATH_TRAVERSAL = "E_PATH_TRAVERSAL"
    E_NO_MANIFEST = "E_NO_MANIFEST"
    E_TIMEOUT = "E_TIMEOUT"
    E_PARSE_FAILED = "E_PARSE_FAILED"
    E_INTERNAL = "E_INTERNAL"


class AnalyzerError(Exception):
    """Raised when analysis cannot continue.

    ``sha256`` and ``file_size`` are set once intake has measured them, so a
    later rejection can still name the report file.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        sha256: str | None = None,
        file_size: int | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.sha256 = sha256
        self.file_size = file_size
        super().__init__(message)
