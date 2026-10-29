"""Process isolation around module-level functions."""

import time

import pytest

from analyzer_core.errors import AnalyzerError, ErrorCode
from analyzer_core.isolation import run_isolated


def _sleep_five():
    time.sleep(5)
    return {"slept": True}


def _raise_value_error():
    raise ValueError("boom")


def _return_dict():
    return {"alpha": 1, "beta": ["x"]}


def test_timeout_stops_long_call():
    started = time.perf_counter()
    with pytest.raises(AnalyzerError) as caught:
        run_isolated(_sleep_five, (), 1)
    elapsed = time.perf_counter() - started
    assert caught.value.code is ErrorCode.E_TIMEOUT
    assert elapsed < 4


def test_child_exception_is_parse_failed():
    with pytest.raises(AnalyzerError) as caught:
        run_isolated(_raise_value_error, (), 10)
    assert caught.value.code is ErrorCode.E_PARSE_FAILED
    assert "ValueError" in caught.value.message


def test_dict_returned_intact():
    assert run_isolated(_return_dict, (), 10) == {"alpha": 1, "beta": ["x"]}
