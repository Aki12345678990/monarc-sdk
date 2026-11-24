"""Pure indicator rules ported from pipeline_v2/indicators_v2.py.

The functions below follow that file's control flow. Resource references that
this process cannot resolve stay unresolved: the component is excluded and the
flag is missing, which is the frozen rule when apktool does not return a boolean.
"""

from __future__ import annotations

import csv
import ipaddress
from functools import lru_cache
from pathlib import Path

from analyzer_core.attribution import classify_cached, host_denied
from analyzer_core.config import reference_dir

PERM_TAGS = ("uses-permission", "uses-permission-sdk-23")
ACTIVITY_LIKE = ("activity", "activity-alias", "service", "receiver")
STORAGE_PERMS = (
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
)
READ_CELL_BROADCASTS = "android.permission.READ_CELL_BROADCASTS"
READ_MEDIA_VISUAL_USER_SELECTED = "android.permission.READ_MEDIA_VISUAL_USER_SELECTED"


class UnclearDefinition(Exception):
    pass


def is_true(val) -> bool:
    return str(val).strip().lower() in ("true", "1")


def is_false(val) -> bool:
    return str(val).strip().lower() in ("false", "0")


def is_absent(val) -> bool:
    return val is None or str(val).strip() == ""


def is_resource_ref(val) -> bool:
    return str(val).strip().startswith("@")


def cast_int(val):
    text = "" if val is None else str(val).strip()
    if text == "":
        return None, "absent"
    try:
        return int(float(text)), "ok"
    except (TypeError, ValueError, OverflowError):
        return None, "uncastable"


def denied_by_list(host, entries) -> bool:
    host = (host or "").lower().rstrip(".")
    for entry in entries:
        if host == entry or host.endswith("." + entry):
            return True
    return False


def load_psl(path: Path) -> dict:
    icann_tlds: set[str] = set()
    normals: set[tuple[str, ...]] = set()
    wildcards: set[tuple[str, ...]] = set()
    exceptions: set[tuple[str, ...]] = set()
    section = None
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            raw_line = line.strip()
            if "===BEGIN ICANN DOMAINS===" in raw_line:
                section = "icann"
                continue
            if "===END ICANN DOMAINS===" in raw_line:
                section = None
                continue
            if "===BEGIN PRIVATE DOMAINS===" in raw_line:
                section = "private"
                continue
            if "===END PRIVATE DOMAINS===" in raw_line:
                section = None
                continue
            if not raw_line or raw_line.startswith("//"):
                continue
            if section not in ("icann", "private"):
                continue
            token = raw_line
            is_exc = token.startswith("!")
            if is_exc:
                token = token[1:]
            is_wild = token.startswith("*.")
            if is_wild:
                token = token[2:]
            token = token.lower().rstrip(".")
            if section == "icann" and "." not in token:
                icann_tlds.add(token)
            labels = tuple(token.split(".")) if token else tuple()
            if is_exc:
                exceptions.add(labels)
            elif is_wild:
                wildcards.add(labels)
            else:
                normals.add(labels)
    return {
        "icann_tlds": icann_tlds,
        "normals": normals,
        "wildcards": wildcards,
        "exceptions": exceptions,
    }


def public_suffix_label_count(labels, psl) -> int:
    labels = tuple(lab.lower() for lab in labels)
    n = len(labels)
    best_exc = -1
    best_other = -1
    for i in range(n):
        suffix = labels[i:]
        if suffix in psl["exceptions"]:
            if len(suffix) > best_exc:
                best_exc = len(suffix)
        if suffix in psl["normals"]:
            if len(suffix) > best_other:
                best_other = len(suffix)
        if i + 1 <= n:
            parent = suffix[1:] if len(suffix) >= 1 else tuple()
            if len(suffix) >= 1 and parent in psl["wildcards"]:
                matched = len(parent) + 1
                if matched > best_other:
                    best_other = matched
    if best_exc >= 0:
        return max(best_exc - 1, 0)
    if best_other >= 0:
        return best_other
    return 1


def registrable_domain(host, psl) -> str:
    host = (host or "").lower().rstrip(".")
    if not host:
        return host
    labels = host.split(".")
    ps_len = public_suffix_label_count(labels, psl)
    need = ps_len + 1
    if need > len(labels):
        return host
    return ".".join(labels[-need:])


def last_label_is_icann_tld(host, psl) -> bool:
    host = (host or "").lower().rstrip(".")
    if not host:
        return False
    last = host.rsplit(".", 1)[-1]
    return last in psl["icann_tlds"]


def parse_ip(host):
    text = (host or "").strip().strip("[]")
    try:
        return ipaddress.ip_address(text)
    except ValueError:
        return None


def accept_host(host, ip_literal, psl, extension_entries, use_extension=True) -> bool:
    host = (host or "").lower().rstrip(".")
    if not host:
        return False
    if host_denied(host):
        return False
    if use_extension and denied_by_list(host, extension_entries):
        return False
    if ip_literal is True or (isinstance(ip_literal, str) and is_true(ip_literal)):
        ip_obj = parse_ip(host)
        if ip_obj is None:
            return False
        return bool(ip_obj.is_global)
    if ip_literal is False or (isinstance(ip_literal, str) and is_false(ip_literal)):
        return last_label_is_icann_tld(host, psl)
    ip_obj = parse_ip(host)
    if ip_obj is not None:
        return bool(ip_obj.is_global)
    return last_label_is_icann_tld(host, psl)


def load_permission_lists(path: Path) -> dict:
    primary: set[str] = set()
    all_set: set[str] = set()
    ext: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            name = row["permission"]
            if str(row.get("include_in_P", "")).strip() == "1":
                primary.add(name)
            all_set.add(name)
            ext.add(name)
    if READ_CELL_BROADCASTS not in all_set:
        all_set.add(READ_CELL_BROADCASTS)
    if READ_MEDIA_VISUAL_USER_SELECTED not in ext:
        ext.add(READ_MEDIA_VISUAL_USER_SELECTED)
    p_all = set(primary)
    p_all.add(READ_CELL_BROADCASTS)
    p_ext = set(primary)
    p_ext.add(READ_MEDIA_VISUAL_USER_SELECTED)
    p_no_storage = set(primary) - set(STORAGE_PERMS)
    return {
        "P": primary,
        "P_all": p_all,
        "P_ext": p_ext,
        "P_declared": set(primary),
        "P_no_storage": p_no_storage,
    }


def declaration_survives_maxsdk(max_sdk_version, min_sdk, ignore_max):
    _mx, status = cast_int(max_sdk_version)
    uncastable = status == "uncastable"
    if ignore_max:
        return True, uncastable
    if status == "absent" or status == "uncastable":
        return True, uncastable
    if min_sdk is None:
        raise UnclearDefinition("min_sdk missing while applying maxSdkVersion")
    return _mx >= min_sdk, uncastable


def compute_p(decls, min_sdk, lists):
    uncastable = 0
    kept = {key: set() for key in lists}
    for item in decls:
        tag = item.get("tag") or ""
        name = item.get("name") or ""
        if tag not in PERM_TAGS:
            continue
        survives, was_uncast = declaration_survives_maxsdk(
            item.get("max_sdk_version"), min_sdk, ignore_max=False
        )
        if was_uncast:
            uncastable += 1
        survives_decl, _ = declaration_survives_maxsdk(
            item.get("max_sdk_version"), min_sdk, ignore_max=True
        )
        for key, allowed in lists.items():
            if name not in allowed:
                continue
            if key == "P_declared":
                if survives_decl:
                    kept[key].add(name)
            elif survives:
                kept[key].add(name)
    return {key: len(value) for key, value in kept.items()}, uncastable, kept


def effective_exported(exported_explicit, has_intent_filter, ctype, target_sdk):
    if is_true(exported_explicit):
        return "yes"
    if is_false(exported_explicit):
        return "no"
    if is_resource_ref(exported_explicit):
        return "resource"
    if not is_absent(exported_explicit):
        return "unclear"
    has_if = is_true(has_intent_filter)
    if ctype in ACTIVITY_LIKE:
        if has_if:
            if target_sdk is None:
                return "unclear"
            if target_sdk >= 31:
                return "anomaly"
            return "yes"
        return "no"
    if ctype == "provider":
        if target_sdk is None:
            return "unclear"
        if target_sdk < 17:
            return "yes"
        return "no"
    return "unclear"


def is_unprotected(ctype, permission, read_permission, write_permission) -> bool:
    if ctype in ACTIVITY_LIKE:
        return is_absent(permission)
    if ctype == "provider":
        return (
            is_absent(permission)
            and is_absent(read_permission)
            and is_absent(write_permission)
        )
    return False


def exported_after_resolution(raw, resolved):
    if is_resource_ref(raw):
        if resolved is None:
            return "exclude_unresolved"
        return resolved
    return raw


def m_exp_decision(
    exported_explicit,
    has_intent_filter,
    ctype,
    target_sdk,
    permission,
    read_permission,
    write_permission,
    launcher,
):
    if is_true(launcher):
        return "exclude_launcher"
    eff = effective_exported(exported_explicit, has_intent_filter, ctype, target_sdk)
    if eff == "anomaly":
        return "anomaly"
    if eff == "unclear":
        return "unclear"
    if eff == "resource":
        return "resource"
    if eff != "yes":
        return "exclude"
    if not is_unprotected(ctype, permission, read_permission, write_permission):
        return "exclude_protected"
    return "count"


def compute_f_debug(debuggable_explicit):
    if debuggable_explicit is None:
        return None
    if is_resource_ref(debuggable_explicit):
        return None
    return 1 if is_true(debuggable_explicit) else 0


def compute_f_backup(allow_backup_explicit):
    if allow_backup_explicit is None:
        return None
    if is_resource_ref(allow_backup_explicit):
        return None
    if is_false(allow_backup_explicit):
        return 0
    return 1


def compute_f_cleartext(nsc_row, uses_cleartext_explicit, target_sdk):
    if nsc_row is not None:
        base_clear = str(nsc_row.get("base_config_cleartext") or "").strip()
        base_present = is_true(nsc_row.get("base_config_present"))
        n_dom_true, _st = cast_int(nsc_row.get("n_domain_config_cleartext_true"))
        if n_dom_true is None:
            n_dom_true = 0
        if target_sdk is None:
            raise UnclearDefinition("target_sdk missing for F_cleartext NSC rule")
        base_true = base_clear == "true" or (
            (base_clear == "absent" or not base_present) and target_sdk <= 27
        )
        return 1 if (base_true or n_dom_true > 0) else 0
    if uses_cleartext_explicit is None or is_resource_ref(uses_cleartext_explicit):
        return None
    if is_absent(uses_cleartext_explicit):
        if target_sdk is None:
            raise UnclearDefinition("target_sdk missing for F_cleartext default")
        return 1 if target_sdk <= 27 else 0
    if is_true(uses_cleartext_explicit):
        return 1
    if is_false(uses_cleartext_explicit):
        return 0
    raise UnclearDefinition(
        "usesCleartextTraffic_explicit is set but is not true or false: %r"
        % (uses_cleartext_explicit,)
    )


def load_api_map(path: Path):
    primary = {}
    conditional = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["class"], row["method"])
            primary[key] = row
            if is_true(row.get("conditional")):
                conditional.add(key)
    return primary, conditional


def compute_a(call_rows, app_id, catalog, cache, primary, axp, conditional):
    """Ported from indicators_v2.compute_a. Reported A is the SDK primary-map count."""

    union_map = set(primary) | set(axp)
    a_pairs = set()
    a_all = set()
    a_union = set()
    a_noncond = set()
    a_calls = 0
    callers: dict[tuple[str, str], dict[str, int]] = {}
    for row in call_rows:
        key = (row["target_class"], row["target_method"])
        in_primary = key in primary
        in_union = key in union_map
        if not in_union:
            continue
        caller = row.get("caller_package") or ""
        cat, sdk_name, _sdk_cat, _fw = classify_cached(caller, app_id, catalog, cache)
        n = int(row["n_callsites"])
        if in_primary:
            a_all.add(key)
        if in_union and cat == "sdk":
            a_union.add(key)
        if in_primary and cat == "sdk":
            a_pairs.add(key)
            a_calls += n
            if key not in conditional:
                a_noncond.add(key)
            bucket = callers.setdefault(key, {})
            label = sdk_name or ""
            bucket[label] = bucket.get(label, 0) + n
    return {
        "A": len(a_pairs),
        "A_calls": a_calls,
        "A_all": len(a_all),
        "A_union": len(a_union),
        "A_noncond": len(a_noncond),
        "callers": callers,
    }


def compute_n(host_recs, app_id, catalog, cache, psl, extension_entries):
    acc = set()
    acc_all = set()
    rows = []
    for item in host_recs:
        host = (item.get("host") or "").lower().rstrip(".")
        caller = item.get("caller_package") or ""
        ip_lit = item.get("ip_literal")
        if ip_lit is None:
            ip_lit = item.get("is_ip_literal")
        if not accept_host(host, ip_lit, psl, extension_entries, use_extension=True):
            continue
        cat, sdk_name, _sdk_cat, _fw = classify_cached(caller, app_id, catalog, cache)
        acc_all.add(host)
        if cat == "sdk":
            acc.add(host)
        rows.append(
            {
                "host": host,
                "caller_package": caller,
                "attribution": cat,
                "sdk_name": sdk_name,
                "ip_literal": ip_lit,
            }
        )
    return {"N": len(acc), "N_all": len(acc_all), "hosts": rows}


@lru_cache(maxsize=1)
def permission_lists() -> dict:
    return load_permission_lists(reference_dir() / "dangerous_permissions_v2.csv")


@lru_cache(maxsize=1)
def api_map():
    return load_api_map(reference_dir() / "sensitive_api_map_v1.csv")


@lru_cache(maxsize=1)
def psl_and_extension():
    psl = load_psl(reference_dir() / "public_suffix_list_9dfbe81.dat")
    entries = []
    path = reference_dir() / "n_host_extension_denylist_v1.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            entries.append((row["host"] or "").lower().rstrip("."))
    return psl, tuple(entries)
