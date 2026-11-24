"""Build data/reference/corpus_v2_values.json from the frozen analysis dataset.

Reads the table stats_v2.py loads for hypotheses.csv (analysis_dataset.csv,
included rows only). Does not write under E:\\AndroZoo. Emits no app identifiers.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reference" / "corpus_v2_values.json"
HEADLINES = ROOT / "web" / "src" / "lib" / "paper-headlines.json"

DATASET = Path(r"E:\AndroZoo\analyzer\results_v2\stats\analysis_dataset.csv")
INDICATORS = Path(r"E:\AndroZoo\analyzer\results_v2\indicators\indicators_v2.csv")
HYPOTHESES = Path(r"E:\AndroZoo\analyzer\results_v2\stats\hypotheses.csv")

COLUMNS = (
    "P",
    "A",
    "N",
    "D",
    "M_exp",
    "M_exp_sdk",
    "n_methods_defined",
    "R",
    "R_minusD",
    "N_all",
)
HYP_IDS = ("H01", "H02", "H03", "H04", "H06")
FORMULA = "(L + (E + 1) / 2) / n"
NOTE = (
    "For corpus apps this equals the frozen rankdata(average)/n exactly; "
    "a new app is placed by the same rule against the unchanged frozen corpus."
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def included(value: str) -> bool:
    return str(value).strip() in {"True", "true", "1"}


def number(raw: str):
    text = (raw or "").strip()
    if text == "":
        return None
    value = float(text)
    if value == int(value) and abs(value) < 1e15:
        return int(value)
    return value


def main() -> None:
    arrays: dict[str, list] = {name: [] for name in COLUMNS}
    n_included = 0
    with DATASET.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if not included(row.get("included", "")):
                continue
            n_included += 1
            for name in COLUMNS:
                value = number(row.get(name, ""))
                if value is not None:
                    arrays[name].append(value)
    if n_included != 1260:
        raise SystemExit(f"included n={n_included}, expected 1260")

    hypotheses = {}
    with HYPOTHESES.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            hid = row["hypothesis"]
            if hid not in HYP_IDS:
                continue
            hypotheses[hid] = {
                "outcome": row["outcome"],
                "n": int(float(row["n"])),
                "rho_p": float(row["rho_p"]),
                "ci95_low": float(row["ci95_low"]),
                "ci95_high": float(row["ci95_high"]),
                "significant": row["significant"] in {"True", "true", "1"},
            }
    missing = [hid for hid in HYP_IDS if hid not in hypotheses]
    if missing:
        raise SystemExit(f"hypotheses missing {missing}")

    metrics = {}
    for name in COLUMNS:
        values = sorted(arrays[name])
        metrics[name] = {"n": len(values), "values": values}

    payload = {
        "name": "v2 included corpus",
        "description": "Sorted indicator values for the 1,260 included research apps.",
        "n_apps": n_included,
        "source": "analysis_dataset.csv",
        "source_role": "stats_v2.load_dataset_rows; hypotheses.csv is computed from these included rows",
        "source_sha256": {
            "analysis_dataset.csv": sha256(DATASET),
            "indicators_v2.csv": sha256(INDICATORS),
            "hypotheses.csv": sha256(HYPOTHESES),
        },
        "percentile_formula": FORMULA,
        "percentile_note": NOTE,
        "metrics": metrics,
        "hypotheses": hypotheses,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    headlines = {
        "percentile_formula": FORMULA,
        "percentile_note": NOTE,
        "n_apps": n_included,
        "hypotheses": hypotheses,
        "parity": None,
    }
    HEADLINES.write_text(json.dumps(headlines, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} apps={n_included}")
    for name, block in metrics.items():
        print(f"  {name} n={block['n']}")


if __name__ == "__main__":
    main()
