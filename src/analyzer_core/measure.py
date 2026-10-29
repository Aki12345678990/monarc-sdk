"""Isolated child entry: extract, classify, and assemble per-APK facts.

Androguard objects never leave this process. The returned dict is picklable.
"""

import ipaddress
import os
import re
import sys
from collections import defaultdict
from urllib.parse import urlsplit

from analyzer_core import v2_constants as cfg
from analyzer_core.attribution import (
    classify_cached,
    dotted_class,
    host_denied,
    load_catalog,
    package_of_class,
)
from analyzer_core.frameworks import frameworks_detected
from analyzer_core.indicators.apis import compute_A
from analyzer_core.indicators.endpoints import compute_N
from analyzer_core.indicators.footprint import CATS, compute_D, pct
from analyzer_core.indicators.manifest import compute_M
from analyzer_core.indicators.permissions import compute_P
from analyzer_core.v2_constants import ANDROID_NS, SERVICE_SDK_CATEGORIES

URL_RE = re.compile(r"""(?i)\b(?:https?|wss?)://[^\s"'<>\\]+""")
HOST_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)
COMPONENT_TAGS = ("activity", "activity-alias", "service", "receiver", "provider")
NSC_TAGS = ("base-config", "domain-config")

_VISIBILITY_CAVEAT = (
    "Code compiled outside DEX (Dart AOT, IL2CPP, JavaScript bundles) is not "
    "visible to the extractor; A and N are lower bounds for framework apps."
)


def record_error(errors, section, exc):
    """Append an exception record.

    Ported from extract_v2.py:50-55 (v2).
    """

    errors.append({
        "section": section,
        "exception_class": type(exc).__name__,
        "message": str(exc),
    })


def to_int_or_none(val):
    """Parse an int or return None.

    Ported from extract_v2.py:58-64 (v2).
    """

    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def is_ip_literal(host):
    """Return True if host is an IPv4/IPv6 literal.

    Ported from extract_v2.py:88-94 (v2).
    """

    h = host.strip("[]")
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        return False


def host_keep(host):
    """Keep IP literals and DNS-looking hosts; no denylist.

    Ported from extract_v2.py:97-105 (v2).
    """

    if not host:
        return False, False
    host = host.lower().rstrip(".")
    if is_ip_literal(host):
        return True, True
    if HOST_RE.match(host) is None:
        return False, False
    return True, False


def android_attr(elem, name, stats):
    """Read an android attribute, namespaced first, then non-namespaced fallback.

    Ported from manifest_v2b.py:44-51 (v2).
    """

    value = elem.get("{%s}%s" % (ANDROID_NS, name))
    if value is None:
        value = elem.get(name)
        if value is not None:
            stats["count"] += 1
            stats["attrs"].add(name)
    return value


def nsc_attr(elem, name):
    """Read an NSC attribute, non-namespaced first.

    Ported from manifest_v2b.py:54-58 (v2).
    """

    value = elem.get(name)
    if value is None:
        value = elem.get("{%s}%s" % (ANDROID_NS, name))
    return value


def resolve_component_name(raw, application_id):
    """Resolve a leading-dot component name against the application id.

    Ported from manifest_v2b.py:35-41 (v2).
    """

    if raw is None:
        return None
    name = str(raw)
    if name.startswith("."):
        return (application_id or "") + name
    return name


def parse_nsc_cleartext(root):
    """True iff any NSC base-config/domain-config permits cleartext.

    Ported from manifest_v2b.py:61-69 (v2).
    """

    found_true = False
    for tag in NSC_TAGS:
        nodes = list(root.findall(".//" + tag)) + list(root.findall(".//{*}" + tag))
        for el in nodes:
            val = nsc_attr(el, "cleartextTrafficPermitted")
            if val == "true":
                found_true = True
    return found_true


def resolve_nsc_path(a, ref):
    """Resolve a networkSecurityConfig resource reference to a zip path.

    Ported from manifest_v2b.py:72-103 (v2).
    """

    if not ref:
        return None, None
    if ref.startswith("@xml/"):
        base = ref[len("@xml/"):]
        names = list(a.zip.namelist())
        stems = [base + ".xml", base]
        for stem in stems:
            if stem in names:
                return stem, "zip_name_@xml"
            suffix = "/" + os.path.basename(stem if stem.endswith(".xml") else stem + ".xml")
            matches = [n for n in names if n.endswith(suffix) and n.startswith("res/")]
            if matches:
                xmlish = [n for n in matches if "/xml" in n]
                return (xmlish[0] if xmlish else matches[0]), "zip_name_@xml"
        raise RuntimeError("could not resolve @xml/ name %r" % (ref,))
    if ref.startswith("@"):
        hexpart = ref[1:]
        if hexpart.lower().startswith("0x"):
            hexpart = hexpart[2:]
        rid = int(hexpart, 16)
        arsc = a.get_android_resources()
        if arsc is None:
            raise RuntimeError("get_android_resources() returned None")
        cfgs = arsc.get_resolved_res_configs(rid)
        if not cfgs:
            raise RuntimeError("get_resolved_res_configs empty for %s" % ref)
        path = cfgs[0][1]
        if not path:
            raise RuntimeError("get_resolved_res_configs returned empty path for %s" % ref)
        return path, "ARSCParser.get_resolved_res_configs"
    raise RuntimeError("unrecognized networkSecurityConfig ref %r" % (ref,))


def join_fw(val):
    """Join detected framework names as aggregate writes them.

    Ported from aggregate_v2.py:36-41 (v2).
    """

    if not val:
        return ""
    if isinstance(val, list):
        return ";".join(str(x) for x in val)
    return str(val)


def _parse_manifest_v2b(a, application_id, errors):
    """Fill overlay manifest fields using v2b attribute semantics.

    Ported from manifest_v2b.py:146-202 (v2).
    """

    from androguard.core.bytecodes.axml import AXMLPrinter

    stats = {"count": 0, "attrs": set()}
    out = {
        "debuggable_explicit": None,
        "allowBackup_explicit": None,
        "usesCleartextTraffic_explicit": None,
        "networkSecurityConfig": None,
        "nsc_parsed": None,
        "nsc_error": None,
        "nsc_cleartextTrafficPermitted_true": None,
        "nsc_resolve_call": None,
        "components": None,
        "ns_fallback_manifest_count": 0,
    }
    try:
        manifest = a.get_android_manifest_xml()
        app = manifest.find("application")
        if app is None:
            out["debuggable_explicit"] = None
            out["allowBackup_explicit"] = None
            out["usesCleartextTraffic_explicit"] = None
            out["networkSecurityConfig"] = None
        else:
            out["debuggable_explicit"] = android_attr(app, "debuggable", stats)
            out["allowBackup_explicit"] = android_attr(app, "allowBackup", stats)
            out["usesCleartextTraffic_explicit"] = android_attr(app, "usesCleartextTraffic", stats)
            out["networkSecurityConfig"] = android_attr(app, "networkSecurityConfig", stats)
        components = []
        for tag in COMPONENT_TAGS:
            for el in manifest.findall(".//" + tag):
                raw_name = android_attr(el, "name", stats)
                resolved = resolve_component_name(raw_name, application_id)
                filters = list(el.findall("intent-filter"))
                is_launcher = False
                for inf in filters:
                    actions = {android_attr(x, "name", stats) for x in inf.findall("action")}
                    cats = {android_attr(x, "name", stats) for x in inf.findall("category")}
                    if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in cats:
                        is_launcher = True
                components.append({
                    "type": tag,
                    "name": resolved,
                    "exported_explicit": android_attr(el, "exported", stats),
                    "has_intent_filter": len(filters) > 0,
                    "permission": android_attr(el, "permission", stats),
                    "readPermission": android_attr(el, "readPermission", stats),
                    "writePermission": android_attr(el, "writePermission", stats),
                    "is_launcher": is_launcher,
                })
        out["components"] = components
    except Exception as e:
        record_error(errors, "manifest", e)

    try:
        ref = out.get("networkSecurityConfig")
        if ref:
            path, call = resolve_nsc_path(a, ref)
            out["nsc_resolve_call"] = call
            data = a.get_file(path)
            root = AXMLPrinter(data).get_xml_obj()
            out["nsc_parsed"] = True
            out["nsc_error"] = None
            out["nsc_cleartextTrafficPermitted_true"] = parse_nsc_cleartext(root)
    except Exception as e:
        if out.get("networkSecurityConfig"):
            out["nsc_parsed"] = False
            out["nsc_error"] = "%s: %s" % (type(e).__name__, e)
            record_error(errors, "networkSecurityConfig", e)

    out["ns_fallback_manifest_count"] = stats["count"]
    return out


def _aggregate(raw, catalog):
    """Per-APK classification and counts. Ported from aggregate_v2.py:162-347 (v2)."""

    app_id = raw.get("package") or ""
    cache = {}
    packages = raw.get("packages") or {}
    native_libs = raw.get("native_libs") or []

    counts = {c: 0 for c in CATS}
    n_service = 0
    sdk_names = set()
    sdk_packages = []
    for pkg, n_classes in packages.items():
        cat, sdk_name, sdk_cat, fw = classify_cached(pkg, app_id, catalog, cache)
        counts[cat] += 1
        if cat == "sdk":
            sdk_packages.append({
                "package": pkg,
                "sdk_name": sdk_name,
                "sdk_category": sdk_cat,
                "n_classes": n_classes,
            })
            if sdk_name:
                sdk_names.add(sdk_name)
            if sdk_cat in SERVICE_SDK_CATEGORIES:
                n_service += 1

    total = sum(counts.values()) if packages else 0
    n_sdk = counts["sdk"]
    n_una = counts["unattributed_third_party"]
    n_tool = counts["toolchain"]
    n_fw = counts["framework"]

    fw_detected, fw_ev = frameworks_detected(list(packages.keys()), native_libs, cfg)

    hosts_all = set()
    hosts_sdk = set()
    hosts_fp = set()
    host_rows = []
    for h in raw.get("hosts") or []:
        host = (h.get("host") or "").lower().rstrip(".")
        if host_denied(host):
            continue
        caller = h.get("caller_package") or ""
        cat, sdk_name, sdk_cat, fw = classify_cached(caller, app_id, catalog, cache)
        ip_lit = h.get("ip_literal")
        if ip_lit is None:
            ip_lit = h.get("is_ip_literal")
        host_rows.append({
            "host": host,
            "caller_package": caller,
            "attribution": cat,
            "sdk_name": sdk_name,
            "ip_literal": ip_lit,
        })
        hosts_all.add(host)
        if cat == "sdk":
            hosts_sdk.add(host)
        if cat == "first_party":
            hosts_fp.add(host)

    inventory = {}
    for rec in sdk_packages:
        name = rec["sdk_name"]
        if not name:
            continue
        key = (name, rec["sdk_category"])
        inventory.setdefault(key, []).append(rec["package"])
    sdk_inventory = [
        {
            "sdk_name": name,
            "sdk_category": category,
            "packages": sorted(pkgs),
        }
        for (name, category), pkgs in sorted(inventory.items(), key=lambda item: (item[0][0] or "", item[0][1] or ""))
    ]

    row = {
        "n_packages_total": total,
        "footprint_strict_pct": pct(n_sdk, total),
        "footprint_inclusive_pct": pct(n_sdk + n_una, total),
        "footprint_strict_nontoolchain_pct": pct(n_sdk, total - n_tool - n_fw),
        "footprint_service_pct": pct(n_service, total),
        "n_sdk_distinct": len(sdk_names),
        "hosts_distinct_all": len(hosts_all),
        "hosts_distinct_sdk": len(hosts_sdk),
        "hosts_distinct_first_party": len(hosts_fp),
        "n_urls_unparseable": raw.get("n_urls_unparseable"),
        "hosts": host_rows,
        "frameworks_detected": join_fw(fw_detected),
        "frameworks_detected_names": list(fw_detected),
        "frameworks_evidence": fw_ev,
        "n_native_libs": len(native_libs),
        "n_dex_files": len(raw.get("dex_files") or []),
        "sdk_inventory": sdk_inventory,
    }
    for cat in CATS:
        row["n_packages_" + cat] = counts[cat]
    return row


def measure_apk(apk_path: str) -> dict:
    """Parse one APK and return picklable extract + aggregate facts.

    Ported from extract_v2.py:168-392 and aggregate_v2.py:151-347 (v2),
    with manifest fields from manifest_v2b.py:146-202 (v2).
    """

    from androguard.misc import AnalyzeAPK
    import androguard

    errors = []
    a, d, dx = AnalyzeAPK(apk_path)

    raw = {
        "package": None,
        "min_sdk": None,
        "target_sdk": None,
        "version_name": None,
        "version_code": None,
        "dex_files": None,
        "total_dex_bytes": None,
        "classes_dex_bytes": None,
        "n_classes": None,
        "n_methods_defined": None,
        "packages": None,
        "native_libs": None,
        "permissions_requested": None,
        "hosts": None,
        "n_urls_unparseable": 0,
        "n_call_rows": None,
        "errors": errors,
        "python_version": sys.version,
        "androguard_version": getattr(androguard, "__version__", None),
    }

    try:
        raw["package"] = a.get_package()
        raw["min_sdk"] = to_int_or_none(a.get_min_sdk_version())
        raw["target_sdk"] = to_int_or_none(a.get_target_sdk_version())
        raw["permissions_requested"] = list(a.get_permissions())
        raw["version_name"] = a.get_androidversion_name()
        raw["version_code"] = a.get_androidversion_code()
    except Exception as e:
        record_error(errors, "apk_meta", e)

    application_id = raw["package"] or ""

    try:
        dex_files = []
        for name in list(a.get_dex_names()):
            data = a.get_file(name)
            dex_files.append({"name": name, "bytes": len(data)})
        raw["dex_files"] = dex_files
        raw["total_dex_bytes"] = sum(x["bytes"] for x in dex_files)
        classes = [x for x in dex_files if x["name"] == "classes.dex"]
        raw["classes_dex_bytes"] = classes[0]["bytes"] if classes else None
    except Exception as e:
        record_error(errors, "dex_files", e)

    try:
        so_bases = set()
        for n in a.zip.namelist():
            parts = n.replace("\\", "/").split("/")
            if len(parts) == 3 and parts[0] == "lib" and parts[2].endswith(".so"):
                so_bases.add(parts[2])
        raw["native_libs"] = sorted(so_bases)
    except Exception as e:
        record_error(errors, "native_libs", e)

    pkg_class_counts = defaultdict(int)
    try:
        n_classes = 0
        n_methods = 0
        for dex in d:
            for cls in dex.get_classes():
                n_classes += 1
                dotted = dotted_class(cls.get_name())
                pkg = package_of_class(dotted)
                pkg_class_counts[pkg] += 1
                for meth in cls.get_methods():
                    if meth.get_code() is not None:
                        n_methods += 1
        raw["n_classes"] = n_classes
        raw["n_methods_defined"] = n_methods
        raw["packages"] = dict(pkg_class_counts)
    except Exception as e:
        record_error(errors, "class_scan", e)

    try:
        n_unparseable = 0
        host_recs = set()
        for dex in d:
            for cls in dex.get_classes():
                caller_pkg = package_of_class(dotted_class(cls.get_name()))
                for meth in cls.get_methods():
                    code = meth.get_code()
                    if code is None:
                        continue
                    for instr in code.get_bc().get_instructions():
                        if instr.get_name() not in ("const-string", "const-string/jumbo"):
                            continue
                        raw_s = instr.get_raw_string()
                        if not raw_s:
                            continue
                        for m in URL_RE.finditer(raw_s):
                            try:
                                parsed = urlsplit(m.group(0))
                                host = (parsed.hostname or "").lower()
                            except ValueError:
                                n_unparseable += 1
                                continue
                            keep, ip_lit = host_keep(host)
                            if not keep:
                                continue
                            host = host.lower().rstrip(".")
                            host_recs.add((host, caller_pkg, ip_lit))
        raw["n_urls_unparseable"] = n_unparseable
        raw["hosts"] = [
            {"host": h, "caller_package": pkg, "ip_literal": ip_lit}
            for (h, pkg, ip_lit) in sorted(host_recs, key=lambda x: (x[0], x[1] or "", x[2]))
        ]
    except Exception as e:
        record_error(errors, "network", e)

    manifest_out = _parse_manifest_v2b(a, application_id, errors)
    raw.update(manifest_out)

    try:
        call_counts = defaultdict(int)
        for ma in dx.get_methods():
            if ma.is_external():
                continue
            caller_pkg = package_of_class(dotted_class(ma.get_method().get_class_name()))
            for _ca, target, _off in ma.get_xref_to():
                tclass = dotted_class(target.get_class_name())
                if not tclass.startswith("android."):
                    continue
                call_counts[(caller_pkg, tclass, target.get_name())] += 1
        call_rows = [
            {
                "caller_package": k[0],
                "target_class": k[1],
                "target_method": k[2],
                "n_callsites": n,
            }
            for k, n in sorted(call_counts.items())
        ]
        raw["n_call_rows"] = len(call_rows)
    except Exception as e:
        record_error(errors, "raw_calls", e)

    catalog = load_catalog()
    agg = _aggregate(raw, catalog)

    fw_names = agg["frameworks_detected_names"]
    fw_ev = agg["frameworks_evidence"]
    frameworks = [
        {"name": name, "evidence": fw_ev.get(name, [])}
        for name in fw_names
    ]

    return {
        "package_name": raw.get("package"),
        "version_name": raw.get("version_name"),
        "version_code": raw.get("version_code"),
        "min_sdk": raw.get("min_sdk"),
        "target_sdk": raw.get("target_sdk"),
        "n_dex_files": agg["n_dex_files"],
        "total_dex_bytes": raw.get("total_dex_bytes"),
        "classes_dex_bytes": raw.get("classes_dex_bytes"),
        "n_classes": raw.get("n_classes"),
        "n_methods_defined": raw.get("n_methods_defined"),
        "n_native_libs": agg["n_native_libs"],
        "n_call_rows": raw.get("n_call_rows"),
        "n_urls_unparseable": raw.get("n_urls_unparseable"),
        "frameworks_detected": agg["frameworks_detected"],
        "frameworks": frameworks,
        "visibility_caveat": _VISIBILITY_CAVEAT if fw_names else None,
        "sdk_inventory": agg["sdk_inventory"],
        "errors": list(errors),
        "python_version": raw.get("python_version"),
        "androguard_version": raw.get("androguard_version"),
        "indicators": {
            "P": compute_P(raw.get("permissions_requested")),
            "A": compute_A(raw.get("n_call_rows")),
            "N": compute_N(
                hosts_distinct_all=agg["hosts_distinct_all"],
                hosts_distinct_sdk=agg["hosts_distinct_sdk"],
                hosts_distinct_first_party=agg["hosts_distinct_first_party"],
                n_urls_unparseable=raw.get("n_urls_unparseable"),
                hosts=agg["hosts"],
            ),
            "M": compute_M(raw),
            "D": compute_D(agg),
        },
        "parity": {
            "min_sdk": raw.get("min_sdk"),
            "target_sdk": raw.get("target_sdk"),
            "n_dex_files": agg["n_dex_files"],
            "total_dex_bytes": raw.get("total_dex_bytes"),
            "classes_dex_bytes": raw.get("classes_dex_bytes"),
            "n_classes": raw.get("n_classes"),
            "n_methods_defined": raw.get("n_methods_defined"),
            "n_native_libs": agg["n_native_libs"],
            "frameworks_detected": agg["frameworks_detected"],
            "n_packages_total": agg["n_packages_total"],
            "n_packages_toolchain": agg["n_packages_toolchain"],
            "n_packages_framework": agg["n_packages_framework"],
            "n_packages_sdk": agg["n_packages_sdk"],
            "n_packages_first_party": agg["n_packages_first_party"],
            "n_packages_obfuscated": agg["n_packages_obfuscated"],
            "n_packages_unattributed_third_party": agg["n_packages_unattributed_third_party"],
            "footprint_strict_pct": agg["footprint_strict_pct"],
            "footprint_inclusive_pct": agg["footprint_inclusive_pct"],
            "footprint_strict_nontoolchain_pct": agg["footprint_strict_nontoolchain_pct"],
            "footprint_service_pct": agg["footprint_service_pct"],
            "n_sdk_distinct": agg["n_sdk_distinct"],
            "hosts_distinct_all": agg["hosts_distinct_all"],
            "hosts_distinct_sdk": agg["hosts_distinct_sdk"],
            "hosts_distinct_first_party": agg["hosts_distinct_first_party"],
            "n_urls_unparseable": raw.get("n_urls_unparseable"),
            "debuggable_explicit": raw.get("debuggable_explicit"),
            "allowBackup_explicit": raw.get("allowBackup_explicit"),
            "usesCleartextTraffic_explicit": raw.get("usesCleartextTraffic_explicit"),
            "networkSecurityConfig": raw.get("networkSecurityConfig"),
            "nsc_parsed": raw.get("nsc_parsed"),
            "nsc_error": raw.get("nsc_error"),
            "nsc_cleartextTrafficPermitted_true": raw.get("nsc_cleartextTrafficPermitted_true"),
            "nsc_resolve_call": raw.get("nsc_resolve_call"),
            "ns_fallback_manifest_count": raw.get("ns_fallback_manifest_count"),
            "n_call_rows": raw.get("n_call_rows"),
        },
    }
