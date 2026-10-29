"""Build data/reference/corpus_v2_univariate.json from the frozen v2 CSVs.

Reads apk_level.csv and analytic_sample.csv from E:\\AndroZoo\\analyzer\\results_v2
(read-only). Keeps rows whose analytic_sample included flag is True. Writes only
per-metric value arrays and aggregate metadata — no app identifiers.
"""

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path(r"E:\AndroZoo\analyzer\results_v2")
APK_LEVEL = SOURCE_DIR / "apk_level.csv"
ANALYTIC_SAMPLE = SOURCE_DIR / "analytic_sample.csv"
OUT = ROOT / "data" / "reference" / "corpus_v2_univariate.json"
EXPECTED_N = 1260
METRICS = ("footprint_strict_pct", "hosts_distinct_all", "n_sdk_distinct")
NAME = "AndroZoo Google Play analytic sample v2"
DESCRIPTION = (
    "1,260 Google Play apps collected by AndroZoo 2022–2024, VirusTotal 0 detections, "
    "stratified by year and APK size (D-001..D-019)"
)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def included_sha256s(path: Path) -> set[str]:
    kept: set[str] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["included"] == "True":
                kept.add(row["sha256"])
    return kept


def collect_metrics(path: Path, keep: set[str]) -> tuple[int, dict[str, list[float]]]:
    values = {name: [] for name in METRICS}
    n_apps = 0
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["sha256"] not in keep:
                continue
            n_apps += 1
            for name in METRICS:
                raw = (row.get(name) or "").strip()
                if raw == "":
                    continue
                values[name].append(round(float(raw), 6))
    for name in METRICS:
        values[name].sort()
    return n_apps, values


def main() -> int:
    if not APK_LEVEL.is_file() or not ANALYTIC_SAMPLE.is_file():
        print(f"Source CSVs not found under {SOURCE_DIR}", file=sys.stderr)
        return 2
    keep = included_sha256s(ANALYTIC_SAMPLE)
    if len(keep) != EXPECTED_N:
        print(
            f"analytic_sample included=True count is {len(keep)}, expected {EXPECTED_N}",
            file=sys.stderr,
        )
        return 2
    n_apps, values = collect_metrics(APK_LEVEL, keep)
    if n_apps != EXPECTED_N:
        print(f"joined apk_level rows: {n_apps}, expected {EXPECTED_N}", file=sys.stderr)
        return 2
    payload = {
        "name": NAME,
        "description": DESCRIPTION,
        "n_apps": n_apps,
        "source_sha256": {
            "apk_level.csv": sha256_file(APK_LEVEL),
            "analytic_sample.csv": sha256_file(ANALYTIC_SAMPLE),
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "metrics": {
            name: {"n": len(values[name]), "values": values[name]} for name in METRICS
        },
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    digest = sha256_file(OUT)
    print(f"wrote {OUT}")
    print(f"n_apps={n_apps}")
    for name in METRICS:
        series = values[name]
        mid = series[len(series) // 2] if series else None
        print(f"  {name}: n={len(series)} min={series[0]} median={mid} max={series[-1]}")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
