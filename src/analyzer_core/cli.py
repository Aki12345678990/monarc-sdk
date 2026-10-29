"""Command line for analyzer_core."""

import argparse
import json
import sys
from importlib.metadata import version as package_version
from pathlib import Path

from analyzer_core import __version__
from analyzer_core.errors import ErrorCode
from analyzer_core.pipeline import analyze
from analyzer_core.reference import verify
from analyzer_core.report import Report

_INTAKE_CODES = {
    ErrorCode.E_NOT_FOUND.value,
    ErrorCode.E_NOT_ZIP.value,
    ErrorCode.E_TOO_LARGE.value,
    ErrorCode.E_ZIP_BOMB.value,
    ErrorCode.E_TOO_MANY_ENTRIES.value,
    ErrorCode.E_PATH_TRAVERSAL.value,
    ErrorCode.E_NO_MANIFEST.value,
}
_PARSE_CODES = {
    ErrorCode.E_TIMEOUT.value,
    ErrorCode.E_PARSE_FAILED.value,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze_parser = sub.add_parser("analyze")
    analyze_parser.add_argument("apk_path")
    analyze_parser.add_argument("--out", dest="out_dir")
    analyze_parser.add_argument("--json", action="store_true")

    sub.add_parser("verify-reference")
    sub.add_parser("version")
    sub.add_parser("schema")

    args = parser.parse_args(argv)
    if args.command == "version":
        print(f"analyzer_core {__version__}")
        print(f"androguard {package_version('androguard')}")
        return 0
    if args.command == "schema":
        sys.stdout.write(json.dumps(Report.model_json_schema(), indent=2, ensure_ascii=False) + "\n")
        return 0
    if args.command == "verify-reference":
        return _verify_reference_command()
    if args.command == "analyze":
        return _analyze_command(args.apk_path, args.out_dir, args.json)
    return 1


def _verify_reference_command() -> int:
    try:
        result = verify()
    except (OSError, UnicodeError) as exc:
        print(f"{type(exc).__name__}: {exc}")
        return 4
    status = result["status"]
    if status == "OK":
        print("OK")
        return 0
    if status == "EMPTY":
        print("EMPTY: No reference data vendored yet (Phase 1B)")
        return 0
    print("MISMATCH")
    for item in result.get("files", []):
        if item.get("match"):
            continue
        print(f"{item.get('path')}: expected {item.get('expected')} actual {item.get('actual')}")
    return 4


def _analyze_command(apk_path: str, out_dir: str | None, as_json: bool) -> int:
    if not as_json and not out_dir:
        print("analyze requires --out or --json", file=sys.stderr)
        return 1
    report = analyze(apk_path)
    code = _exit_code(report)
    if as_json:
        sys.stdout.write(report.to_json())
        return code
    assert out_dir is not None
    _write_report(report, Path(out_dir))
    return code


def _write_report(report: Report, out_dir: Path) -> None:
    sha256 = report.input.sha256
    if not sha256:
        print(report.to_json(), file=sys.stderr)
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{sha256}.json").write_text(report.to_json(), encoding="utf-8")
    (out_dir / f"{sha256}.md").write_text(report.to_markdown(), encoding="utf-8")


def _exit_code(report: Report) -> int:
    if report.status == "ok":
        return 0
    if not report.errors:
        return 1
    code = report.errors[0].code
    if code in _INTAKE_CODES:
        return 2
    if code in _PARSE_CODES:
        return 3
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
