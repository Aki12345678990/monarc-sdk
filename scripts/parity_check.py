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

INDICATOR_COLS = [
    "P",
    "A",
    "N",
    "N_all",
    "D",
    "M_exp",
    "M_exp_sdk",
    "F_debug",
    "F_backup",
    "F_cleartext",
    "M_flags",
    "R",
    "R_minusD",
]
FLOAT_INDICATORS = {"D", "R", "R_minusD"}

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


def indicator_live(measured):
    indicators = measured["indicators"]
    from analyzer_core.report import IndicatorBlock, IndicatorResult
    from analyzer_core.composite import build_composite

    block = IndicatorBlock(
        **{name: IndicatorResult(**indicators[name]) for name in "PANDM"}
    )
    composite = build_composite(block, measured.get("n_methods_defined"))
    details_n = indicators["N"].get("details") or {}
    details_m = indicators["M"].get("details") or {}
    return {
        "P": indicators["P"].get("value"),
        "A": indicators["A"].get("value"),
        "N": indicators["N"].get("value"),
        "N_all": details_n.get("N_all"),
        "D": indicators["D"].get("value"),
        "M_exp": details_m.get("M_exp"),
        "M_exp_sdk": details_m.get("M_exp_sdk"),
        "F_debug": details_m.get("F_debug"),
        "F_backup": details_m.get("F_backup"),
        "F_cleartext": details_m.get("F_cleartext"),
        "M_flags": details_m.get("M_flags"),
        "R": composite.get("R"),
        "R_minusD": composite.get("R_minusD"),
    }


def as_number(raw):
    if raw is None or str(raw).strip() == "":
        return None
    return float(raw)


def indicators_agree(left, right, sha):
    mismatches = []
    for col in INDICATOR_COLS:
        a = as_number(left.get(col))
        b = as_number(right.get(col))
        if a is None and b is None:
            continue
        if a is None or b is None or abs(a - b) > 1e-9:
            mismatches.append((sha, col, left.get(col), right.get(col)))
    return mismatches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk-level", required=True)
    parser.add_argument("--analytic", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--apk-dir", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--indicators", required=True)
    parser.add_argument("--n-per-stratum", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    apk_rows = load_csv(args.apk_level)
    analytic_rows = load_csv(args.analytic)
    dataset = {(r.get("sha256") or "").upper(): r for r in load_csv(args.dataset)}
    frozen_indicators = {(r.get("sha256") or "").upper(): r for r in load_csv(args.indicators)}
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

    table_disagreements = []
    for sha in picked:
        table_disagreements.extend(
            indicators_agree(dataset.get(sha, {}), frozen_indicators.get(sha, {}), sha)
        )
    if table_disagreements:
        print("frozen tables disagree; stopping before the engine run")
        for sha, col, left, right in table_disagreements:
            print("%s %s analysis_dataset=%r indicators_v2=%r" % (sha[:12], col, left, right))
        return 2

    timeout_s = parse_timeout_s()
    matched = {col: 0 for col in COMPARE_COLS}
    total = {col: 0 for col in COMPARE_COLS}
    ind_matched = {col: 0 for col in INDICATOR_COLS}
    ind_total = {col: 0 for col in INDICATOR_COLS}
    ind_max = {col: 0.0 for col in INDICATOR_COLS}
    mismatches = []
    result_rows = []

    for sha in picked:
        v2 = by_sha[sha]
        truth = dataset[sha]
        apk_path = os.path.join(args.apk_dir, sha + ".apk")
        measured = run_isolated(measure_apk, (apk_path,), timeout_s)
        engine = measured["parity"]
        live = indicator_live(measured)
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
        for col in INDICATOR_COLS:
            ind_total[col] += 1
            frozen = as_number(truth.get(col))
            got = live.get(col)
            got_num = None if got is None else float(got)
            if frozen is None and got_num is None:
                diff = 0.0
                ok_ind = True
            elif frozen is None or got_num is None:
                diff = float("inf")
                ok_ind = False
            else:
                diff = abs(got_num - frozen)
                ok_ind = diff <= 1e-9
            if ok_ind:
                ind_matched[col] += 1
            else:
                mismatches.append((sha, col, truth.get(col), got))
            if diff != float("inf") and diff > ind_max[col]:
                ind_max[col] = diff
            row[col + "_dataset"] = truth.get(col)
            row[col + "_engine"] = got
            row[col + "_match"] = ok_ind
        result_rows.append(row)
        print("done", sha, flush=True)

    print("seed", args.seed)
    print("n_sampled", len(picked))
    print("column matched/total")
    for col in COMPARE_COLS:
        print("%s %s/%s" % (col, matched[col], total[col]))
    print("indicator column n_compared n_matching max_abs_diff")
    for col in INDICATOR_COLS:
        print("%s %s %s %s" % (col, ind_total[col], ind_matched[col], ind_max[col]))
    print("mismatches")
    for sha, col, v2_val, eng_val in mismatches:
        print("%s %s v2=%r engine=%r" % (sha[:12], col, v2_val, eng_val))
    result_path = out_dir / "parity_result.csv"
    fieldnames = ["sha256"]
    for col in COMPARE_COLS:
        fieldnames.extend([col + "_v2", col + "_engine", col + "_match"])
    for col in INDICATOR_COLS:
        fieldnames.extend([col + "_dataset", col + "_engine", col + "_match"])
    with result_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in result_rows:
            writer.writerow(row)
    if any(ind_matched[col] != ind_total[col] for col in INDICATOR_COLS):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
