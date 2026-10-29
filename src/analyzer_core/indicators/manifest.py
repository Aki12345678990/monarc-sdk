"""M indicator.

v2 records raw manifest facts only. Ported field set from aggregate_v2.py:323-331
and ns_fallback_manifest_count from manifest_v2b.py:201 / aggregate_v2.py:341.
"""

_M_KEYS = (
    "debuggable_explicit",
    "allowBackup_explicit",
    "usesCleartextTraffic_explicit",
    "networkSecurityConfig",
    "nsc_parsed",
    "nsc_error",
    "nsc_cleartextTrafficPermitted_true",
    "nsc_resolve_call",
    "ns_fallback_manifest_count",
    "components",
)


def compute_M(raw: dict) -> dict:
    """Return M as not_implemented with raw v2 overlay fields.

    Ported from aggregate_v2.py:323-331,341 and manifest_v2b.py:114-202 (v2).
    """

    details = {key: raw.get(key) for key in _M_KEYS}
    return {
        "status": "not_implemented",
        "value": None,
        "reason": "v2 records raw manifest facts only; no misconfiguration flags are defined",
        "definition_source": None,
        "details": details,
    }
