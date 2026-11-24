"""Percentile formula and exposure-index arithmetic."""

from analyzer_core.composite import FORMULA_R, FORMULA_R_MINUS_D, build_composite, percentile
from analyzer_core.report import IndicatorBlock, IndicatorResult


def _average_rank_over_n(value, corpus):
    ranks = []
    ordered = sorted(corpus)
    i = 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1] == ordered[i]:
            j += 1
        average = ((i + 1) + (j + 1)) / 2
        for _ in range(i, j + 1):
            ranks.append(average)
        i = j + 1
    paired = sorted(zip(ordered, ranks))
    for item, rank in paired:
        if item == value:
            return rank / len(corpus)
    raise AssertionError(value)


def _indicator(value, status="ok", details=None):
    return IndicatorResult(status=status, value=value, details=details or {})


def test_percentile_ties_and_new_value_not_inserted():
    corpus = [1.0, 2.0, 2.0, 2.0, 3.0]
    assert percentile(2, corpus) == (1 + (3 + 1) / 2) / 5
    assert percentile(2, corpus) == _average_rank_over_n(2.0, corpus)
    # 2.5 is not inserted: L=4, E=0, n stays 5.
    assert percentile(2.5, corpus) == (4 + (0 + 1) / 2) / 5
    assert percentile(None, corpus) is None


def test_exposure_arithmetic_and_missing_indicator(monkeypatch):
    corpus = {
        "n_apps": 4,
        "percentile_formula": "(L + (E + 1) / 2) / n",
        "metrics": {
            name: {"n": 4, "values": [1, 2, 3, 4]}
            for name in ("P", "A", "N", "D", "M_exp", "M_exp_sdk", "n_methods_defined", "R", "R_minusD", "N_all")
        },
    }
    monkeypatch.setattr(
        "analyzer_core.composite.load_values",
        lambda: (corpus, "abc"),
    )
    indicators = IndicatorBlock(
        P=_indicator(1),
        A=_indicator(2),
        N=_indicator(3),
        M=_indicator(0, details={"M_exp": 4, "M_exp_sdk": 1}),
        D=_indicator(4),
    )
    built = build_composite(indicators, n_methods_defined=2)
    pr = built["percentiles"]
    assert built["R"] == 0.25 * pr["P"] + 0.25 * pr["A"] + 0.25 * pr["N"] + 0.25 * pr["D"]
    assert built["R_minusD"] == (pr["P"] + pr["A"] + pr["N"]) / 3
    assert built["formula_R"] == FORMULA_R
    assert built["formula_R_minusD"] == FORMULA_R_MINUS_D
    assert pr["P"] == _average_rank_over_n(1, [1, 2, 3, 4])

    missing = IndicatorBlock(
        P=_indicator(None, status="unavailable"),
        A=_indicator(2),
        N=_indicator(3),
        M=_indicator(0, details={"M_exp": 1, "M_exp_sdk": 0}),
        D=_indicator(4),
    )
    blocked = build_composite(missing, n_methods_defined=2)
    assert blocked["R"] is None
    assert blocked["R_minusD"] is None
    assert blocked["reason"] == "Missing indicator: P"
