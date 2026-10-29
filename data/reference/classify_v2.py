import csv
import ipaddress
import os
import re

from config_v2 import HOST_DENYLIST, SDK_CATALOG_CSV, SDK_CATEGORY_VOCABULARY

HOST_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)


def load_catalog(path=None):
    if path is None:
        path = SDK_CATALOG_CSV
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        kept = [ln for ln in f if ln.strip() and not ln.lstrip().startswith("#")]
    for row in csv.DictReader(kept):
        mt = (row.get("match_type") or "prefix").strip() or "prefix"
        rows.append({
            "prefix": row["prefix"],
            "sdk_name": row["sdk_name"],
            "category": row["category"],
            "source": row.get("source", ""),
            "match_type": mt,
        })
    return rows


def validate_catalog(catalog=None, cfg=None):
    if catalog is None:
        catalog = load_catalog()
    vocab = cfg.SDK_CATEGORY_VOCABULARY if cfg is not None else SDK_CATEGORY_VOCABULARY
    violations = []
    seen = set()
    for row in catalog:
        pref = row["prefix"]
        mt = row.get("match_type") or "prefix"
        cat = row["category"]
        if mt == "prefix" and not (pref.endswith(".") or pref.endswith("_")):
            violations.append(
                "prefix-type row %r does not end with '.' or '_'" % (pref,)
            )
        if mt == "exact" and pref.endswith("."):
            violations.append("exact-type row %r has a trailing dot" % (pref,))
        pair = (pref, mt)
        if pair in seen:
            violations.append("duplicate (prefix, match_type): %r %r" % pair)
        seen.add(pair)
        if cat not in vocab:
            violations.append(
                "category %r not in vocabulary for prefix %r" % (cat, pref)
            )
    if violations:
        raise ValueError(
            "catalog validation failed (%d):\n%s"
            % (len(violations), "\n".join(violations))
        )
    return True


def is_ip_literal(host):
    h = (host or "").strip("[]")
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        return False


def host_denied(host):
    host = (host or "").lower().rstrip(".")
    for entry in HOST_DENYLIST:
        if host == entry or host.endswith("." + entry):
            return True
    return False


def host_ok(host):
    if not host:
        return False, False
    host = host.lower().rstrip(".")
    if is_ip_literal(host):
        return True, True
    if HOST_RE.match(host) is None:
        return False, False
    if host_denied(host):
        return False, False
    return True, False


def package_of_class(dotted):
    if not dotted:
        return ""
    parts = dotted.split(".")
    final = parts[-1]
    if "$" in final:
        parts[-1] = final.split("$", 1)[0]
    if len(parts) <= 1:
        return ""
    return ".".join(parts[:-1])


def classify_package(package, app_id, catalog, cfg):
    package = package or ""
    key = package + "."
    for p in cfg.TOOLCHAIN_PREFIXES:
        if key.startswith(p):
            return "toolchain", None, None, None, None
    for fw_name, prefixes in cfg.FRAMEWORK_PREFIXES.items():
        for p in prefixes:
            if p.endswith("."):
                if key.startswith(p):
                    return "framework", None, None, fw_name, None
            elif p == "crc64":
                first = package.split(".")[0] if package else ""
                if first.startswith("crc64"):
                    return "framework", None, None, fw_name, None
    if app_id:
        if package == app_id or package.startswith(app_id + "."):
            return "first_party", None, None, None, "exact"
    for row in catalog:
        if row.get("match_type") == "exact" and package == row["prefix"]:
            return "sdk", row["sdk_name"], row["category"], None, None
    prefix_rows = [r for r in catalog if r.get("match_type") != "exact"]
    prefix_rows.sort(key=lambda r: -len(r["prefix"]))
    for row in prefix_rows:
        pref = row["prefix"]
        if not (pref.endswith(".") or pref.endswith("_")):
            pref = pref + "."
        if key.startswith(pref):
            return "sdk", row["sdk_name"], row["category"], None, None
    if app_id:
        two = ".".join(app_id.split(".")[:2])
        if two and key.startswith(two + "."):
            return "first_party", None, None, None, "dev"
    segs = package.split(".") if package else [""]
    if all(len(s) <= 2 for s in segs):
        return "obfuscated", None, None, None, None
    return "unattributed_third_party", None, None, None, None


def frameworks_detected(packages, native_libs, cfg):
    evidence = {name: set() for name in cfg.FRAMEWORK_PREFIXES}
    for pkg in packages:
        key = (pkg or "") + "."
        first = (pkg.split(".")[0] if pkg else "")
        for fw_name, prefixes in cfg.FRAMEWORK_PREFIXES.items():
            for p in prefixes:
                if p.endswith(".") and key.startswith(p):
                    evidence[fw_name].add("package_prefix:" + p)
                elif p == "crc64" and first.startswith("crc64"):
                    evidence[fw_name].add("package_prefix:crc64")
    libs = set(native_libs or [])
    for fw_name, libnames in cfg.FRAMEWORK_NATIVE_LIBS.items():
        for lib in libnames:
            if lib in libs:
                evidence[fw_name].add("native_lib:" + lib)
    detected = []
    ev_out = {}
    for fw_name in cfg.FRAMEWORK_PREFIXES:
        ev = sorted(evidence[fw_name])
        if ev:
            detected.append(fw_name)
            ev_out[fw_name] = ev
    return detected, ev_out
