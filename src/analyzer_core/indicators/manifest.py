"""M indicator.

Ported from indicators_v2.py effective_exported, m_exp_decision and the flag
functions. M_exp_sdk is the primary value. Flags are separate from component counts.
"""

from analyzer_core.indicators.v2_rules import (
    UnclearDefinition,
    compute_f_backup,
    compute_f_cleartext,
    compute_f_debug,
    exported_after_resolution,
    is_resource_ref,
    m_exp_decision,
)


def compute_M(components, target_sdk, raw, nsc_row) -> dict:
    """Count effectively exported, unprotected, non-launcher components."""

    try:
        return _compute(components or [], target_sdk, raw or {}, nsc_row)
    except UnclearDefinition as exc:
        return {
            "status": "unavailable",
            "value": None,
            "reason": str(exc),
            "definition_source": "indicators_v2.py:m_exp_decision",
            "details": {},
        }


def _compute(components, target_sdk, raw, nsc_row) -> dict:
    counted = []
    m_exp = 0
    m_exp_sdk = 0
    notes = []
    for component in components:
        raw_exported = component.get("exported_explicit")
        resolved = component.get("exported_resolved")
        exp_attr = exported_after_resolution(raw_exported, resolved)
        if exp_attr == "exclude_unresolved":
            notes.append(
                "excluded_unresolved_exported:%s:%s"
                % (component.get("type"), component.get("name"))
            )
            continue
        decision = m_exp_decision(
            exp_attr,
            component.get("has_intent_filter"),
            component.get("type"),
            target_sdk,
            component.get("permission"),
            component.get("readPermission"),
            component.get("writePermission"),
            component.get("is_launcher"),
        )
        if decision == "anomaly":
            notes.append(
                "m_exp_anomaly:%s:%s" % (component.get("type"), component.get("name"))
            )
            continue
        if decision == "unclear":
            raise UnclearDefinition(
                "exported rule unclear type=%s name=%s exported=%r"
                % (component.get("type"), component.get("name"), raw_exported)
            )
        if decision != "count":
            continue
        m_exp += 1
        attribution = component.get("attribution")
        if attribution == "sdk":
            m_exp_sdk += 1
        counted.append(
            {
                "name": component.get("name"),
                "type": component.get("type"),
                "sdk_name": component.get("sdk_name") or "",
                "attribution": attribution,
                "protection": "none",
            }
        )

    debug_raw = raw.get("debuggable_explicit")
    backup_raw = raw.get("allowBackup_explicit")
    uct_raw = raw.get("usesCleartextTraffic_explicit")
    debug_val = raw.get("debuggable_resolved") if is_resource_ref(debug_raw) else debug_raw
    backup_val = raw.get("allowBackup_resolved") if is_resource_ref(backup_raw) else backup_raw
    uct_val = raw.get("usesCleartextTraffic_resolved") if is_resource_ref(uct_raw) else uct_raw
    f_debug = compute_f_debug(debug_val)
    f_backup = compute_f_backup(backup_val)
    if nsc_row is None and (raw.get("networkSecurityConfig") or "").strip():
        f_cleartext = None
        notes.append("F_cleartext_missing_unrecoverable_nsc")
    else:
        f_cleartext = compute_f_cleartext(nsc_row, uct_val, target_sdk)
    m_flags = None
    if None not in (f_debug, f_backup, f_cleartext):
        m_flags = f_debug + f_backup + f_cleartext
    return {
        "status": "ok",
        "value": m_exp_sdk,
        "reason": None,
        "definition_source": "indicators_v2.py:m_exp_decision",
        "details": {
            "M_exp": m_exp,
            "M_exp_sdk": m_exp_sdk,
            "F_debug": f_debug,
            "F_backup": f_backup,
            "F_cleartext": f_cleartext,
            "M_flags": m_flags,
            "components": counted,
            "notes": notes,
        },
    }
