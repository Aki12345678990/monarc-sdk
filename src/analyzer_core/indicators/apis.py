"""A indicator.

Ported from indicators_v2.py compute_a. Callers are classified with the frozen
attribution classifier.
"""

from analyzer_core.indicators.v2_rules import api_map, compute_a


def compute_A(call_rows, app_id, catalog) -> dict:
    """Distinct mapped (class, method) pairs invoked by SDK-attributed callers."""

    primary, conditional = api_map()
    result = compute_a(call_rows or [], app_id, catalog, {}, primary, {}, conditional)
    pairs = []
    for key in sorted(result["callers"]):
        row = primary[key]
        callers = [
            {"sdk_name": name, "n_callsites": count}
            for name, count in sorted(result["callers"][key].items())
        ]
        pairs.append(
            {
                "class": key[0],
                "method": key[1],
                "permission": row.get("dangerous_permissions") or "",
                "callers": callers,
            }
        )
    return {
        "status": "ok",
        "value": result["A"],
        "reason": None,
        "definition_source": "indicators_v2.py:compute_a",
        "details": {
            "pairs": pairs,
            "A_calls": result["A_calls"],
            "A_all": result["A_all"],
            "A_noncond": result["A_noncond"],
        },
    }
