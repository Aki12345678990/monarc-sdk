"""Assemble a report from intake and isolated measurement."""

import os

from analyzer_core.config import parse_timeout_s
from analyzer_core.errors import AnalyzerError, ErrorCode
from analyzer_core.intake import validate
from analyzer_core.isolation import run_isolated
from analyzer_core.measure import measure_apk
from analyzer_core.report import (
    IndicatorBlock,
    IndicatorResult,
    Report,
    ReportError,
    ReportInput,
)


def analyze(apk_path: str | os.PathLike[str]) -> Report:
    """Validate ``apk_path``, measure in a child process, and return a report."""

    sha256: str | None = None
    file_size: int | None = None
    try:
        accepted = validate(apk_path)
        sha256 = accepted.sha256
        file_size = accepted.file_size
        measured = run_isolated(measure_apk, (os.fspath(apk_path),), parse_timeout_s())
        indicators = measured.get("indicators") or {}
        return Report(
            status="ok",
            errors=[],
            input=ReportInput(
                sha256=accepted.sha256,
                file_size=accepted.file_size,
                package_name=measured.get("package_name"),
                version_name=measured.get("version_name"),
                version_code=measured.get("version_code"),
                min_sdk=measured.get("min_sdk"),
                target_sdk=measured.get("target_sdk"),
            ),
            frameworks=measured.get("frameworks") or [],
            visibility_caveat=measured.get("visibility_caveat"),
            sdk_inventory=measured.get("sdk_inventory") or [],
            indicators=_indicator_block(indicators),
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


def _indicator_block(raw: dict) -> IndicatorBlock:
    def item(name: str) -> IndicatorResult:
        payload = raw.get(name) or {}
        return IndicatorResult(
            status=payload.get("status", "not_implemented"),
            value=payload.get("value"),
            reason=payload.get("reason"),
            definition_source=payload.get("definition_source"),
            details=payload.get("details") or {},
        )

    return IndicatorBlock(
        P=item("P"),
        A=item("A"),
        N=item("N"),
        M=item("M"),
        D=item("D"),
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
