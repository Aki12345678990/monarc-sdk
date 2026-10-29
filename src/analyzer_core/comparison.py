"""Univariate corpus comparison. One metric at a time; no pairing of indicators."""

from __future__ import annotations

import hashlib
import json
from bisect import bisect_left, bisect_right
from pathlib import Path
from typing import Any

from analyzer_core.config import reference_dir
from analyzer_core.reference import verify
from analyzer_core.report import (
    COMPARISON_NOTE,
    COMPARISON_UNAVAILABLE,
    Comparison,
    ComparisonMetrics,
    CorpusInfo,
    Histogram,
    IndicatorBlock,
    IndicatorResult,
    MetricComparison,
)

CORPUS_FILENAME = "corpus_v2_univariate.json"

def percentile_midrank(value: float | int | None, sorted_values: list[float]) -> float | None:
    """100 * (count_less + 0.5 * count_equal) / n. None if value is None or the series is empty."""

    if value is None or not sorted_values:
        return None
    number = float(value)
    n = len(sorted_values)
    count_less = bisect_left(sorted_values, number)
    count_equal = bisect_right(sorted_values, number) - count_less
    return 100.0 * (count_less + 0.5 * count_equal) / n


def histogram(
    sorted_values: list[float],
    value: float | int | None,
    bins: int = 20,
) -> Histogram:
    """Equal-width bins over [min, max]. If min==max, one bin. app_bin is clamped to the range."""

    if not sorted_values:
        return Histogram(edges=[], counts=[], app_bin=None)
    lo = float(sorted_values[0])
    hi = float(sorted_values[-1])
    if lo == hi:
        app_bin = 0 if value is not None else None
        return Histogram(edges=[lo, hi], counts=[len(sorted_values)], app_bin=app_bin)

    width = (hi - lo) / bins
    edges = [lo + i * width for i in range(bins)] + [hi]
    counts = [0] * bins
    for item in sorted_values:
        counts[_bin_index(float(item), lo, hi, width, bins)] += 1
    app_bin = None if value is None else _bin_index(float(value), lo, hi, width, bins)
    return Histogram(edges=edges, counts=counts, app_bin=app_bin)


def _bin_index(value: float, lo: float, hi: float, width: float, bins: int) -> int:
    if value <= lo:
        return 0
    if value >= hi:
        return bins - 1
    index = int((value - lo) / width)
    return min(max(index, 0), bins - 1)


def corpus_path() -> Path:
    return reference_dir() / CORPUS_FILENAME


def load_corpus() -> tuple[dict[str, Any], str] | None:
    """Return (payload, sha256 of the corpus file) if MANIFEST verification succeeds."""

    result = verify()
    if result["status"] != "OK":
        return None
    path = corpus_path()
    listed = any(item.get("path") == CORPUS_FILENAME and item.get("match") for item in result["files"])
    if not listed or not path.is_file():
        return None
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or "metrics" not in payload:
        return None
    digest = hashlib.sha256(raw).hexdigest()
    return payload, digest


def compare_indicator_block(indicators: IndicatorBlock) -> tuple[Comparison | None, str | None]:
    """Build a comparison block, or (None, COMPARISON_UNAVAILABLE) if the corpus cannot be loaded."""

    loaded = load_corpus()
    if loaded is None:
        return None, COMPARISON_UNAVAILABLE
    payload, digest = loaded
    metrics_src = payload.get("metrics") or {}
    d_ok = indicators.D.status == "ok"
    n_ok = indicators.N.status == "ok"
    return (
        Comparison(
            corpus=CorpusInfo(
                name=payload["name"],
                description=payload["description"],
                n_apps=int(payload["n_apps"]),
                reference_sha256=digest,
            ),
            metrics=ComparisonMetrics(
                D=_metric(indicators.D, "footprint_strict_pct", metrics_src) if d_ok else None,
                N=_metric(indicators.N, "hosts_distinct_all", metrics_src) if n_ok else None,
                n_sdk_distinct=_sdk_distinct_metric(indicators.D, metrics_src) if d_ok else None,
            ),
            note=COMPARISON_NOTE,
        ),
        None,
    )


def _series(metrics_src: dict, field: str) -> list[float]:
    block = metrics_src.get(field) or {}
    raw = block.get("values") or []
    return [float(item) for item in raw]


def _metric(indicator: IndicatorResult, field: str, metrics_src: dict) -> MetricComparison | None:
    values = _series(metrics_src, field)
    if not values:
        return None
    value = indicator.value
    return MetricComparison(
        source_field=field,
        value=value,
        percentile=percentile_midrank(value, values),
        n=len(values),
        histogram=histogram(values, value),
    )


def _sdk_distinct_metric(d_indicator: IndicatorResult, metrics_src: dict) -> MetricComparison | None:
    values = _series(metrics_src, "n_sdk_distinct")
    if not values:
        return None
    raw = (d_indicator.details or {}).get("n_sdk_distinct")
    value: float | int | None
    if isinstance(raw, (int, float)):
        value = raw
    else:
        value = None
    return MetricComparison(
        source_field="n_sdk_distinct",
        value=value,
        percentile=percentile_midrank(value, values),
        n=len(values),
        histogram=histogram(values, value),
    )
