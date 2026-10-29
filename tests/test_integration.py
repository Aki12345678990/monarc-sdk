"""End-to-end analyze() against ANALYZER_TEST_APK when set."""

import json
import os
import re

import pytest

from analyzer_core.pipeline import analyze
from analyzer_core.report import LIMITATIONS

_FORBIDDEN_KEY = re.compile(r"score|tier|verdict|risk|rating|grade", re.IGNORECASE)
_FORBIDDEN_VALUE = re.compile(
    r"critical|malicious|safe\b|risk score|rating|grade",
    re.IGNORECASE,
)


pytestmark = pytest.mark.skipif(
    not os.environ.get("ANALYZER_TEST_APK"),
    reason="ANALYZER_TEST_APK is unset",
)


def test_analyze_test_apk():
    report = analyze(os.environ["ANALYZER_TEST_APK"])
    payload = json.loads(report.to_json())
    assert payload["status"] == "ok"
    for key in (
        "schema_version",
        "engine",
        "input",
        "status",
        "errors",
        "frameworks",
        "visibility_caveat",
        "sdk_inventory",
        "indicators",
        "comparison",
        "comparison_reason",
        "limitations",
    ):
        assert key in payload
    assert payload["schema_version"] == "1.1.0"
    assert payload["comparison"] is not None
    assert payload["comparison_reason"] is None
    d_pct = payload["comparison"]["metrics"]["D"]["percentile"]
    n_pct = payload["comparison"]["metrics"]["N"]["percentile"]
    assert isinstance(d_pct, (int, float)) and 0.0 <= d_pct <= 100.0
    assert isinstance(n_pct, (int, float)) and 0.0 <= n_pct <= 100.0
    assert payload["limitations"] == list(LIMITATIONS)
    indicators = payload["indicators"]
    assert indicators["D"]["status"] == "ok"
    assert indicators["N"]["status"] == "ok"
    assert indicators["P"]["status"] == "not_implemented"
    assert indicators["M"]["status"] == "not_implemented"
    assert indicators["A"]["status"] == "unavailable"
    _assert_clean(payload)


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
