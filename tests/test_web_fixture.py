"""The web UI's synthetic fixture report must validate against the engine's Report model."""

import json
from pathlib import Path

from analyzer_core.report import Report

_FIXTURE = Path(__file__).resolve().parents[1] / "web" / "src" / "test" / "fixtures" / "report.json"


def test_web_fixture_validates_against_report_model():
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    report = Report.model_validate(payload)
    assert report.status == "ok"
    assert set(payload) == set(Report.model_fields)
