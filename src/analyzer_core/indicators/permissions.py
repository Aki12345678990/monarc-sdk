"""P indicator.

Ported from extract_v2.py:225 (v2). v2 has no dangerous-permission definition.
"""


def compute_P(manifest_permissions: list[str] | None) -> dict:
    """Return P as not_implemented with the sorted requested-permission list.

    Ported from extract_v2.py:225 (v2).
    """

    requested = sorted(manifest_permissions or [])
    return {
        "status": "not_implemented",
        "value": None,
        "reason": "No dangerous-permission definition exists in the frozen v2 pipeline",
        "definition_source": None,
        "details": {"permissions_requested": requested},
    }
