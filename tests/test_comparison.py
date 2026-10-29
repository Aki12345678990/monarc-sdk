"""Univariate corpus comparison: percentile, histogram, and the vendored corpus file."""

import json
import re
from pathlib import Path

from analyzer_core.comparison import (
    CORPUS_FILENAME,
    compare_indicator_block,
    corpus_path,
    histogram,
    percentile_midrank,
)
from analyzer_core.report import (
    COMPARISON_NOTE,
    COMPARISON_UNAVAILABLE,
    IndicatorBlock,
    IndicatorResult,
    Report,
)
from analyzer_core import __version__
from analyzer_service.storage import current_report_key

_HEX64 = re.compile(r"\b[0-9a-f]{64}\b", re.IGNORECASE)
_ALLOWED_TOP = {
    "name",
    "description",
    "n_apps",
    "source_sha256",
    "generated_at",
    "metrics",
}
_ALLOWED_METRIC = {"n", "values"}
_ALLOWED_SOURCE = {"apk_level.csv", "analytic_sample.csv"}
_FORBIDDEN_KEY = re.compile(r"score|tier|verdict|risk|rating|grade", re.IGNORECASE)
_FORBIDDEN_VALUE = re.compile(
    r"critical|malicious|safe\b|risk score|rating|grade",
    re.IGNORECASE,
)


def test_percentile_below_min_is_zero():
    assert percentile_midrank(-1, [0.0, 1.0, 2.0]) == 0.0


def test_percentile_above_max_is_hundred():
    assert percentile_midrank(10, [0.0, 1.0, 2.0]) == 100.0


def test_percentile_exact_ties():
    # 1 below, 3 equal, 1 above → (1 + 0.5*3) / 5 * 100 = 50
    assert percentile_midrank(2, [1.0, 2.0, 2.0, 2.0, 3.0]) == 50.0


def test_percentile_empty_or_none():
    assert percentile_midrank(1.0, []) is None
    assert percentile_midrank(None, [1.0, 2.0]) is None


def test_histogram_twenty_bins_sum_and_app_bin():
    values = [float(i) for i in range(21)]  # 0..20 inclusive
    middle = histogram(values, 10.0, bins=20)
    assert len(middle.edges) == 21
    assert len(middle.counts) == 20
    assert sum(middle.counts) == 21
    assert middle.app_bin == 10

    at_min = histogram(values, 0.0, bins=20)
    assert at_min.app_bin == 0
    at_max = histogram(values, 20.0, bins=20)
    assert at_max.app_bin == 19
    below = histogram(values, -5.0, bins=20)
    assert below.app_bin == 0
    above = histogram(values, 99.0, bins=20)
    assert above.app_bin == 19


def test_histogram_min_equals_max_is_one_bin():
    result = histogram([3.0, 3.0, 3.0], 3.0)
    assert result.edges == [3.0, 3.0]
    assert result.counts == [3]
    assert result.app_bin == 0


def test_corpus_file_shape_and_no_app_identifiers():
    path = corpus_path()
    assert path.name == CORPUS_FILENAME
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert set(payload) == _ALLOWED_TOP
    assert set(payload["source_sha256"]) == _ALLOWED_SOURCE
    assert set(payload["metrics"]) == {
        "footprint_strict_pct",
        "hosts_distinct_all",
        "n_sdk_distinct",
    }
    for name, block in payload["metrics"].items():
        assert set(block) == _ALLOWED_METRIC, name
        assert block["n"] == len(block["values"])
        assert block["values"] == sorted(block["values"])
    text = path.read_text(encoding="utf-8")
    found = set(_HEX64.findall(text))
    allowed = set(payload["source_sha256"].values())
    assert found == allowed


def test_comparison_on_synthetic_ok_report():
    indicators = IndicatorBlock(
        P=IndicatorResult(status="not_implemented"),
        A=IndicatorResult(status="unavailable"),
        N=IndicatorResult(status="ok", value=4, details={"hosts_distinct_all": 4}),
        M=IndicatorResult(status="not_implemented"),
        D=IndicatorResult(
            status="ok",
            value=12.5,
            details={"footprint_strict_pct": 12.5, "n_sdk_distinct": 3},
        ),
    )
    comparison, reason = compare_indicator_block(indicators)
    assert reason is None
    assert comparison is not None
    report = Report(status="ok", indicators=indicators, comparison=comparison, comparison_reason=reason)
    payload = json.loads(report.to_json())
    assert payload["schema_version"] == "1.1.0"
    assert payload["comparison"] is not None
    assert payload["comparison_reason"] is None
    assert payload["comparison"]["note"] == COMPARISON_NOTE
    d = payload["comparison"]["metrics"]["D"]
    n = payload["comparison"]["metrics"]["N"]
    sdk = payload["comparison"]["metrics"]["n_sdk_distinct"]
    assert d["source_field"] == "footprint_strict_pct"
    assert n["source_field"] == "hosts_distinct_all"
    assert sdk["source_field"] == "n_sdk_distinct"
    for metric in (d, n, sdk):
        assert 0.0 <= metric["percentile"] <= 100.0
        assert metric["n"] == 1260
        assert len(metric["histogram"]["counts"]) == 20
        assert sum(metric["histogram"]["counts"]) == metric["n"]
    _assert_clean(payload)


def test_comparison_unavailable_when_reference_dir_empty(tmp_path, monkeypatch):
    (tmp_path / "MANIFEST.sha256").write_text("", encoding="utf-8")
    monkeypatch.setenv("ANALYZER_REFERENCE_DIR", str(tmp_path))
    indicators = IndicatorBlock(
        P=IndicatorResult(status="not_implemented"),
        A=IndicatorResult(status="unavailable"),
        N=IndicatorResult(status="ok", value=1),
        M=IndicatorResult(status="not_implemented"),
        D=IndicatorResult(status="ok", value=1.0, details={"n_sdk_distinct": 1}),
    )
    comparison, reason = compare_indicator_block(indicators)
    assert comparison is None
    assert reason == COMPARISON_UNAVAILABLE


def test_report_key_includes_engine_version():
    key = current_report_key("0" * 64)
    assert f"__{__version__}__" in key


def _assert_clean(obj) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            assert _FORBIDDEN_KEY.search(str(key)) is None
            if key == "limitations":
                continue
            _assert_clean(value)
        return
    if isinstance(obj, list):
        for item in obj:
            _assert_clean(item)
        return
    if isinstance(obj, str):
        assert _FORBIDDEN_VALUE.search(obj) is None
