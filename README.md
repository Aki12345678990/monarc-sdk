# analyzer_core

analyzer_core is a static analyzer for Android APK files. It checks the archive, reads package and SDK metadata, and writes a JSON report and a Markdown report.

It does not execute APK code. It does not produce a composite score, a 0–100 score, a tier, or a malware verdict.

## Current state

D and N implemented and parity-validated against the frozen v2 pipeline; A unavailable (API map not finalised); P and M not implemented (no v2 definition); report shows raw permissions and raw manifest facts.

## Windows setup

```
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m pip install -e .
```

## CLI

```
analyzer analyze <apk_path> --out <dir>
analyzer analyze <apk_path> --json
analyzer verify-reference
analyzer version
```

`python -m analyzer_core` accepts the same commands.

`analyze --out` writes `<sha256>.json` and `<sha256>.md` in the given directory. `--json` prints the JSON report to stdout and does not write those files. `verify-reference` prints `OK`, `MISMATCH`, or `EMPTY`. `version` prints the analyzer_core version and the installed androguard version.

Exit codes:

- 0: the command finished and, for `analyze`, the report status is ok
- 2: the file was rejected at intake
- 3: parse failed or timed out
- 1: internal error
- 4: reference data verification failed

## androguard pin

androguard is pinned at 3.3.5 so measurements stay comparable with the research corpus.

## Tests

```
.venv\Scripts\python -m pytest -q
```

Tests build synthetic ZIP archives in a temporary directory. They do not use APK files.
