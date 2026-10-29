"""A indicator.

Raw android.* xref extraction is ported; the SEED API map is not applied.
"""


def compute_A(n_call_rows: int | None) -> dict:
    """Return A as unavailable, with n_call_rows only.

    Ported from extract_v2.py:363-384 (v2).
    """

    return {
        "status": "unavailable",
        "value": None,
        "reason": "Sensitive API map (API 28–33) not finalised",
        "definition_source": "extract_v2.py:363-384",
        "details": {"n_call_rows": n_call_rows},
    }
