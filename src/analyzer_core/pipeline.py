"""Assemble a report from intake and isolated metadata. Stubs are not called."""

import os

from analyzer_core.config import parse_timeout_s
from analyzer_core.errors import AnalyzerError, ErrorCode
from analyzer_core.intake import validate
from analyzer_core.isolation import run_isolated
from analyzer_core.metadata import extract_metadata
from analyzer_core.report import Report, ReportError, ReportInput


def analyze(apk_path: str | os.PathLike[str]) -> Report:
    """Validate ``apk_path``, parse metadata in a child process, and return a report.

    Indicator, framework, and SDK-inventory fields stay at their Phase 1A
    placeholders. Intake and parse failures still return a report.
    """

    sha256: str | None = None
    file_size: int | None = None
    try:
        accepted = validate(apk_path)
        sha256 = accepted.sha256
        file_size = accepted.file_size
        meta = run_isolated(extract_metadata, (os.fspath(apk_path),), parse_timeout_s())
        return Report(
            status="ok",
            errors=[],
            input=ReportInput(
                sha256=accepted.sha256,
                file_size=accepted.file_size,
                package_name=meta.get("package_name"),
                version_name=meta.get("version_name"),
                version_code=meta.get("version_code"),
                min_sdk=meta.get("min_sdk"),
                target_sdk=meta.get("target_sdk"),
            ),
        )
    except AnalyzerError as exc:
        return _error_report(
            exc,
            sha256=exc.sha256 if exc.sha256 is not None else sha256,
            file_size=exc.file_size if exc.file_size is not None else file_size,
        )
    except Exception as exc:
        return _error_report(
            AnalyzerError(ErrorCode.E_INTERNAL, f"{type(exc).__name__}: {exc}"),
            sha256=sha256,
            file_size=file_size,
        )


def _error_report(
    exc: AnalyzerError,
    *,
    sha256: str | None,
    file_size: int | None,
) -> Report:
    return Report(
        status="error",
        errors=[ReportError(code=exc.code.value, message=exc.message)],
        input=ReportInput(sha256=sha256, file_size=file_size),
    )
