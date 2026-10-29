"""D indicator.

Ported from aggregate_v2.py:51-54,167-197,311-315 (v2).
"""

CATS = (
    "toolchain",
    "framework",
    "sdk",
    "first_party",
    "obfuscated",
    "unattributed_third_party",
)


def pct(num, den):
    """100.0 * num / den, or None if den is 0/None.

    Ported from aggregate_v2.py:51-54 (v2).
    """

    if den is None or den == 0:
        return None
    return 100.0 * float(num) / float(den)


def compute_D(agg: dict) -> dict:
    """Return D as footprint_strict_pct with namespace-breadth details.

    Ported from aggregate_v2.py:51-54,167-197,311-315 (v2).
    """

    details = {
        "n_packages_total": agg["n_packages_total"],
        "footprint_strict_pct": agg["footprint_strict_pct"],
        "footprint_inclusive_pct": agg["footprint_inclusive_pct"],
        "footprint_strict_nontoolchain_pct": agg["footprint_strict_nontoolchain_pct"],
        "footprint_service_pct": agg["footprint_service_pct"],
        "n_sdk_distinct": agg["n_sdk_distinct"],
        "note": "namespace breadth, not code volume; lower bound in obfuscated apps",
    }
    for cat in CATS:
        details["n_packages_" + cat] = agg["n_packages_" + cat]
    return {
        "status": "ok",
        "value": agg["footprint_strict_pct"],
        "reason": None,
        "definition_source": "aggregate_v2.py:51-54,167-197,311-315",
        "details": details,
    }
