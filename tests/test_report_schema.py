"""Report schema constraints for Phase 1A."""

import json
import re

from analyzer_core.report import Report

_REQUIRED = [
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
]

_LIMITATIONS = [
    "Static analysis only; no code was executed.",
    "SDK attribution is namespace-based.",
    "Obfuscation can hide SDK code, so SDK findings are a lower bound.",
    "Cross-platform framework code may not be visible to DEX analysis.",
    "No runtime behaviour was observed.",
    "This is not a malware verdict.",
]

_FORBIDDEN_KEY = re.compile(r"score|tier|verdict|risk", re.IGNORECASE)
_FORBIDDEN_VALUE = re.compile(r"critical|malicious|safe\b", re.IGNORECASE)


def test_default_report_has_required_fields():
    payload = json.loads(Report().to_json())
    for key in _REQUIRED:
        assert key in payload
    assert payload["schema_version"] == "1.0.0"
    assert payload["comparison"] is None
    assert payload["comparison_reason"] == (
        "Corpus comparison deferred until research validation is complete."
    )
    assert payload["limitations"] == _LIMITATIONS
    assert set(payload["indicators"]) == {"P", "A", "N", "M", "D"}


def test_serialized_report_has_no_score_language():
    payload = json.loads(Report().to_json())
    _assert_clean(payload)


def test_indicators_not_implemented():
    payload = json.loads(Report().to_json())
    for name in ("P", "A", "N", "M", "D"):
        indicator = payload["indicators"][name]
        assert indicator["status"] == "not_implemented"
        assert indicator["value"] is None
        assert indicator["reason"] == "Awaiting Phase 1B port from frozen v2 pipeline"
        assert indicator["definition_source"] is None
        assert indicator["details"] == {}


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
