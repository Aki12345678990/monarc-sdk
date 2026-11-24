"""P indicator.

Ported from indicators_v2.py compute_p and extract_supp_v2.py permission rows.
"""

from analyzer_core.indicators.v2_rules import (
    PERM_TAGS,
    UnclearDefinition,
    compute_p,
    declaration_survives_maxsdk,
    permission_lists,
)


def compute_P(declarations, min_sdk) -> dict:
    """Distinct dangerous permissions from uses-permission and uses-permission-sdk-23.

    A declaration whose maxSdkVersion is below minSdkVersion is not counted.
    """

    try:
        lists = permission_lists()
        counts, uncastable, kept = compute_p(declarations or [], min_sdk, lists)
    except UnclearDefinition as exc:
        return {
            "status": "unavailable",
            "value": None,
            "reason": str(exc),
            "definition_source": "indicators_v2.py:compute_p",
            "details": {},
        }
    tags_for: dict[str, list[str]] = {}
    for item in declarations or []:
        tag = item.get("tag") or ""
        name = item.get("name") or ""
        if tag not in PERM_TAGS or name not in kept["P"]:
            continue
        survives, _uncast = declaration_survives_maxsdk(
            item.get("max_sdk_version"), min_sdk, ignore_max=False
        )
        if not survives:
            continue
        bucket = tags_for.setdefault(name, [])
        if tag not in bucket:
            bucket.append(tag)
    permissions = [
        {"name": name, "tags": tags_for.get(name, [])}
        for name in sorted(kept["P"])
    ]
    return {
        "status": "ok",
        "value": counts["P"],
        "reason": None,
        "definition_source": "indicators_v2.py:compute_p",
        "details": {
            "permissions": permissions,
            "P_all": counts["P_all"],
            "P_ext": counts["P_ext"],
            "P_declared": counts["P_declared"],
            "P_no_storage": counts["P_no_storage"],
            "n_uncastable_maxsdk": uncastable,
        },
    }
