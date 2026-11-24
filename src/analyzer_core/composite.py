"""Exposure index from corpus percentile ranks.

percentile(x, corpus) = (L + (E + 1) / 2) / n
L = count of corpus values < x, E = count of corpus values == x, n = len(corpus).

For corpus apps this equals the frozen rankdata(average)/n exactly; a new app
is placed by the same rule against the unchanged frozen corpus. The value is
not inserted and the divisor stays n.
"""

from __future__ import annotations

import hashlib
import json
from bisect import bisect_left, bisect_right
from pathlib import Path

from analyzer_core.config import reference_dir
from analyzer_core.reference import verify
from analyzer_core.report import IndicatorBlock

VALUES_FILENAME = "corpus_v2_values.json"
PERCENTILE_FORMULA = "(L + (E + 1) / 2) / n"
FORMULA_R = "0.25*pr(P)+0.25*pr(A)+0.25*pr(N)+0.25*pr(D)"
FORMULA_R_MINUS_D = "(pr(P)+pr(A)+pr(N))/3"
_RANK_KEYS = ("P", "A", "N", "D", "M_exp", "M_exp_sdk", "n_methods_defined")


def percentile(x, corpus) -> float | None:
    """Mid-rank of x against an unchanged frozen corpus array."""

    if x is None or not corpus:
        return None
    number = float(x)
    n = len(corpus)
    less = bisect_left(corpus, number)
    equal = bisect_right(corpus, number) - less
    return (less + (equal + 1) / 2) / n


def load_values() -> tuple[dict, str] | None:
    result = verify()
    if result["status"] != "OK":
        return None
    path = reference_dir() / VALUES_FILENAME
    listed = any(item.get("path") == VALUES_FILENAME and item.get("match") for item in result["files"])
    if not listed or not path.is_file():
        return None
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return None
    digest = hashlib.sha256(raw).hexdigest()
    return payload, digest


def build_composite(indicators: IndicatorBlock, n_methods_defined) -> dict:
    """R and R_minusD. Either is null when one of its inputs is missing."""

    loaded = load_values()
    if loaded is None:
        return _null("Corpus reference unavailable")
    payload, digest = loaded
    metrics = payload.get("metrics") or {}
    series = {name: _series(metrics, name) for name in _RANK_KEYS}
    values = {
        "P": _indicator_value(indicators.P),
        "A": _indicator_value(indicators.A),
        "N": _indicator_value(indicators.N),
        "D": _indicator_value(indicators.D),
        "M_exp": _detail_number(indicators.M, "M_exp"),
        "M_exp_sdk": _detail_number(indicators.M, "M_exp_sdk"),
        "n_methods_defined": n_methods_defined if isinstance(n_methods_defined, (int, float)) else None,
    }
    ranks = {name: percentile(values[name], series[name]) for name in _RANK_KEYS}
    missing = [name for name in ("P", "A", "N", "D") if ranks[name] is None]
    reason = None
    exposure = None
    without_d = None
    if missing:
        reason = "Missing indicator: " + ", ".join(missing)
    else:
        exposure = 0.25 * ranks["P"] + 0.25 * ranks["A"] + 0.25 * ranks["N"] + 0.25 * ranks["D"]
        without_d = (ranks["P"] + ranks["A"] + ranks["N"]) / 3
    n_by = {name: len(series[name]) for name in _RANK_KEYS}
    return {
        "R": exposure,
        "R_minusD": without_d,
        "reason": reason,
        "percentiles": ranks,
        "size_percentile": ranks["n_methods_defined"],
        "formula_R": FORMULA_R,
        "formula_R_minusD": FORMULA_R_MINUS_D,
        "percentile_formula": payload.get("percentile_formula") or PERCENTILE_FORMULA,
        "corpus_n": int(payload.get("n_apps") or 0),
        "reference_sha256": digest,
        "n_by_indicator": n_by,
    }


def _series(metrics: dict, name: str) -> list[float]:
    block = metrics.get(name) or {}
    return [float(item) for item in (block.get("values") or [])]


def _indicator_value(indicator):
    if indicator.status != "ok":
        return None
    value = indicator.value
    if isinstance(value, (int, float)):
        return value
    return None


def _detail_number(indicator, key: str):
    if indicator.status != "ok":
        return None
    raw = (indicator.details or {}).get(key)
    if isinstance(raw, (int, float)):
        return raw
    return None


def _null(reason: str) -> dict:
    return {
        "R": None,
        "R_minusD": None,
        "reason": reason,
        "percentiles": {name: None for name in _RANK_KEYS},
        "size_percentile": None,
        "formula_R": FORMULA_R,
        "formula_R_minusD": FORMULA_R_MINUS_D,
        "percentile_formula": PERCENTILE_FORMULA,
        "corpus_n": 0,
        "reference_sha256": "",
        "n_by_indicator": {},
    }


def values_path() -> Path:
    return reference_dir() / VALUES_FILENAME
