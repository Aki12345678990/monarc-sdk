# Phase 0 — RECON

Date: 2026-10-29

## Critical

The research pipeline path `E:\AndroZoo\analyzer\` is not accessible. Drive `E:` does not exist on this machine. No freeze manifest could be read, so no per-file SHA256 MATCH / MISMATCH result exists. Sections 0.3–0.5 are **Cannot determine**.

No alternate path was adopted. `extract_v2.py` was not found under `C:\Users\akile\OneDrive`, `C:\Users\akile\Documents`, `C:\Users\akile\Downloads`, or `D:\`.

---

## 0.1 ROOT check

- Absolute path: `C:\Users\akile\OneDrive\Desktop\Monarc-sdk`
- `dir /a` contents: empty (only `.` and `..`). No `.git/`, `.cursor/`, or `.vscode/`. No other files or directories at the time of the check (before `docs\` was created for this file).
- ROOT is not inside `E:\AndroZoo\analyzer\`.
- Empty-ROOT check: passed. Work continued.

## 0.2 Environment

Install nothing in this phase. Nothing was installed.

| Item | Result |
| --- | --- |
| OS | Microsoft Windows NT 10.0.26300.0 (`win32 10.0.26300`) |
| `py -0p` | `-V:3.12 *        C:\Users\akile\AppData\Local\Programs\Python\Python312\python.exe` |
| Python 3.12 available | Yes. `py -3.12` reports `3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]`. It is the only interpreter listed by `py -0p`, and it is the default (`*`). |
| git | `git version 2.45.1.windows.1` |
| docker | not installed (`docker` is not recognized as a command) |

Mounted filesystem drives: `C:` (Windows, NTFS), `D:` (NTFS, nearly empty: `$RECYCLE.BIN`, `Huawei Share`, `System Volume Information`). No drive letter `E:`. `subst` produced no mappings. `net use` listed no connections.

## 0.3 v2 research artefacts

Specified root: `E:\AndroZoo\analyzer\`

Access result: **Cannot determine**. `Get-ChildItem` on `E:\AndroZoo\analyzer` failed with `DriveNotFoundException` (`Cannot find drive. A drive with the name 'E' does not exist`).

| Item | Absolute path | Size | SHA256 | Notes |
| --- | --- | --- | --- | --- |
| a) `extract_v2.py` | Cannot determine | Cannot determine | Cannot determine | Not readable |
| a) `classify_v2.py` | Cannot determine | Cannot determine | Cannot determine | Not readable |
| a) `run_extract_v2.py` | Cannot determine | Cannot determine | Cannot determine | Not readable |
| a) `aggregate_v2.py` | Cannot determine | Cannot determine | Cannot determine | Not readable |
| a) any other `*_v2.py` | Cannot determine | Cannot determine | Cannot determine | Directory listing failed |
| b) frozen SDK catalog (~484 data rows) | Cannot determine | Cannot determine | Cannot determine | Row count: Cannot determine. Header: Cannot determine |
| c) freeze manifest | Cannot determine | Cannot determine | Cannot determine | No listed files to re-hash. No MATCH / MISMATCH rows. |
| d) sensitive-API map files (name contains `sensitive_api_map`) | Cannot determine | Cannot determine | Cannot determine | Row count and header: Cannot determine. Which file `aggregate_v2.py` / config points at: Cannot determine |
| e) dangerous-permission list used for P | Cannot determine | — | — | Source/location: Cannot determine (file or in-code constant unknown) |
| f) framework detection logic | Cannot determine | — | — | Cannot determine |
| g) blinded attribution validation set | Cannot determine | — | — | Path, row count, header: Cannot determine. Rows were not printed. |
| h) `docs\decision_log.md` | Cannot determine | — | — | Highest D-number: Cannot determine. Entry titles: Cannot determine |
| i) test files (e.g. `test_classify.py`) | Cannot determine | — | — | Test names: Cannot determine |
| j) v2 results (apk-level table and per-APK outputs) | Cannot determine | — | — | Path, row count, header: Cannot determine. Rows were not printed. |

No research script was executed. No `.lock` file was touched. No secret was read or copied.

## 0.4 Function inventory (`extract_v2.py`, `classify_v2.py`)

Cannot determine. Neither file could be opened, so no function name, signature, purpose, side effect, hardcoded path, or import-safety (top-level code) check was performed.

## 0.5 Indicator implementations (exact v2 code)

No indicator definition was invented. Exact v2 code was not available to quote.

| Indicator | File + lines | Computation |
| --- | --- | --- |
| P dangerous permissions | Cannot determine | Cannot determine |
| A sensitive API invocations (SDK-attributed namespaces or not) | Cannot determine | Cannot determine. Whether A is restricted to SDK-attributed namespaces: Cannot determine |
| N network endpoints/hosts | Cannot determine | Cannot determine |
| M manifest misconfiguration flags | Cannot determine | Flag list: Cannot determine |
| D SDK footprint and companion fields (`n_sdk_distinct`, obfuscated share, service footprint) | Cannot determine | Formula: Cannot determine |
| Classifier category ordering (`toolchain`, `framework`, `first_party_exact`, `sdk`, `first_party_dev`, `obfuscated`, `unattributed_third_party`) | Cannot determine | Cannot determine |

## 0.6 Files created in Phase 0

Only this file:

- `C:\Users\akile\OneDrive\Desktop\Monarc-sdk\docs\RECON.md`

`docs\` was created so this file could be written. Nothing under `E:\AndroZoo\` was created, modified, moved, renamed, or deleted.

---

## Blockers

1. **Drive `E:` is not present.** `E:\AndroZoo\analyzer\` cannot be listed or read. Volumes visible: `C:` (Windows), `D:` (empty data volume), plus unlabeled recovery/OEM volumes (WINPE, Onekey, WinRE) with no drive letter. No `subst` mapping and no `net use` connection.
2. **Freeze manifest unavailable.** SHA256 recomputation of frozen pipeline / catalog / config files was not possible. No MATCH or MISMATCH can be reported.
3. **All v2 artefacts unavailable:** `*_v2.py`, frozen SDK catalog, sensitive-API map(s) and which one config points at, dangerous-permission list, framework detection, validation-set path/header/row count, `decision_log.md` D-numbers and titles, test names, and v2 results tables.
4. **Function-level port inventory and indicator quotations were not produced** because the source files could not be opened.
5. **`extract_v2.py` was not found** in `C:\Users\akile\OneDrive`, `C:\Users\akile\Documents`, `C:\Users\akile\Downloads`, or `D:\`. A machine-wide search was not used to pick a substitute tree. If the corpus lives on removable media, that volume needs to be mounted as `E:` (or the prompt must name the real path). This recon does not authorize any other location.
6. **Phase 1 was not started.** No venv, no vendored reference data, no engine code, no git commit.

Ambiguities that would still need a decision even after the drive is mounted: none can be evaluated until the tree at the specified path can be read.
