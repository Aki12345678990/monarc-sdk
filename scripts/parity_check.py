"""Compare analyzer_core measure_apk output to v2 apk_level.csv."""

import argparse
import csv
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analyzer_core.config import parse_timeout_s
from analyzer_core.isolation import run_isolated
from analyzer_core.measure import measure_apk

FLOAT_COLS = {
    "footprint_strict_pct",
    "footprint_inclusive_pct",
    "footprint_strict_nontoolchain_pct",
    "footprint_service_pct",
}

BOOL_COLS = {
    "nsc_parsed",
    "nsc_cleartextTrafficPermitted_true",
}

COMPARE_COLS = [
    "min_sdk",
    "target_sdk",
    "n_dex_files",
    "total_dex_bytes",
    "classes_dex_bytes",
    "n_classes",
    "n_methods_defined",
    "n_native_libs",
    "frameworks_detected",
    "n_packages_total",
    "n_packages_toolchain",
    "n_packages_framework",
    "n_packages_sdk",
    "n_packages_first_party",
    "n_packages_obfuscated",
    "n_packages_unattributed_third_party",
    "footprint_strict_pct",
    "footprint_inclusive_pct",
    "footprint_strict_nontoolchain_pct",
    "footprint_service_pct",
    "n_sdk_distinct",
    "hosts_distinct_all",
    "hosts_distinct_sdk",
    "hosts_distinct_first_party",
    "n_urls_unparseable",
    "debuggable_explicit",
    "allowBackup_explicit",
    "usesCleartextTraffic_explicit",
    "networkSecurityConfig",
    "nsc_parsed",
    "nsc_error",
    "nsc_cleartextTrafficPermitted_true",
    "nsc_resolve_call",
    "ns_fallback_manifest_count",
    "n_call_rows",
]


def load_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def included_true(val):
    return str(val).strip() in {"True", "true", "1"}


def v2_norm(col, raw):
    if raw is None:
        return ""
    text = str(raw)
    if text == "":
        return ""
    if col in BOOL_COLS:
        return text
    if col in FLOAT_COLS:
        return round(float(text), 6)
    # pandas to_csv emits "47.0" for int columns that mixed with None.
    try:
        number = float(text)
    except ValueError:
        return text
    if number == int(number):
        return str(int(number))
    return text


def engine_norm(col, val):
    if val is None:
        return ""
    if col in BOOL_COLS:
        if val is True:
            return "True"
        if val is False:
            return "False"
        return ""
    if col in FLOAT_COLS:
        return round(float(val), 6)
    if isinstance(val, bool):
        return "True" if val else "False"
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    return str(val)


def sample_shas(apk_rows, analytic_rows, validation_path, n_per_stratum, seed):
    included = {
        (r.get("sha256") or "").upper()
        for r in analytic_rows
        if included_true(r.get("included"))
    }
    validation = load_csv(validation_path)
    excluded = {(r.get("sha256") or "").upper() for r in validation}
    by_stratum = {}
    for r in apk_rows:
        sha = (r.get("sha256") or "").upper()
        if sha not in included or sha in excluded:
            continue
        stratum = r.get("stratum") or ""
        by_stratum.setdefault(stratum, []).append(sha)
    rng = random.Random(seed)
    picked = []
    for stratum in sorted(by_stratum):
        cands = sorted(set(by_stratum[stratum]))
        k = min(n_per_stratum, len(cands))
        picked.extend(rng.sample(cands, k))
    return picked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk-level", required=True)
    parser.add_argument("--analytic", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--apk-dir", required=True)
    parser.add_argument("--n-per-stratum", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    apk_rows = load_csv(args.apk_level)
    analytic_rows = load_csv(args.analytic)
    picked = sample_shas(
        apk_rows, analytic_rows, args.validation, args.n_per_stratum, args.seed
    )
    by_sha = {(r.get("sha256") or "").upper(): r for r in apk_rows}

    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    sample_path = out_dir / "parity_sample.txt"
    sample_path.write_text(
        "seed=%s\n" % args.seed + "\n".join(picked) + "\n",
        encoding="utf-8",
    )

    timeout_s = parse_timeout_s()
    matched = {col: 0 for col in COMPARE_COLS}
    total = {col: 0 for col in COMPARE_COLS}
    mismatches = []
    result_rows = []

    for sha in picked:
        v2 = by_sha[sha]
        apk_path = os.path.join(args.apk_dir, sha + ".apk")
        measured = run_isolated(measure_apk, (apk_path,), timeout_s)
        engine = measured["parity"]
        row = {"sha256": sha}
        for col in COMPARE_COLS:
            total[col] += 1
            v2_val = v2_norm(col, v2.get(col))
            eng_val = engine_norm(col, engine.get(col))
            ok = v2_val == eng_val
            if ok:
                matched[col] += 1
            else:
                mismatches.append((sha, col, v2_val, eng_val))
            row[col + "_v2"] = v2_val
            row[col + "_engine"] = eng_val
            row[col + "_match"] = ok
        result_rows.append(row)
        print("done", sha, flush=True)

    print("seed", args.seed)
    print("n_sampled", len(picked))
    print("column matched/total")
    for col in COMPARE_COLS:
        print("%s %s/%s" % (col, matched[col], total[col]))
    print("mismatches")
    for sha, col, v2_val, eng_val in mismatches:
        print("%s %s v2=%r engine=%r" % (sha, col, v2_val, eng_val))

    result_path = out_dir / "parity_result.csv"
    fieldnames = ["sha256"]
    for col in COMPARE_COLS:
        fieldnames.extend([col + "_v2", col + "_engine", col + "_match"])
    with result_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in result_rows:
            writer.writerow(row)


if __name__ == "__main__":
    main()
