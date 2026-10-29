"""Package attribution and host helpers. Ported from classify_v2.py (v2)."""

import csv
import ipaddress
import re

from analyzer_core import v2_constants as cfg
from analyzer_core.config import reference_dir
from analyzer_core.v2_constants import HOST_DENYLIST, SDK_CATEGORY_VOCABULARY

HOST_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)


def load_catalog(path=None):
    """Load SDK catalog rows, skipping comments and blank lines.

    Ported from classify_v2.py:13-28 (v2).
    """

    if path is None:
        path = str(reference_dir() / "sdk_catalog.csv")
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
    validate_catalog(rows, cfg)
    return rows


def validate_catalog(catalog=None, cfg=None):
    """Check prefix/exact shape, duplicates, and category vocabulary.

    Ported from classify_v2.py:31-60 (v2).
    """

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
    """Return True if host is an IPv4/IPv6 literal.

    Ported from classify_v2.py:63-69 (v2).
    """

    h = (host or "").strip("[]")
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        return False


def host_denied(host):
    """Return True if host matches HOST_DENYLIST exactly or as a suffix.

    Ported from classify_v2.py:72-77 (v2).
    """

    host = (host or "").lower().rstrip(".")
    for entry in HOST_DENYLIST:
        if host == entry or host.endswith("." + entry):
            return True
    return False


def host_ok(host):
    """Keep IP literals and DNS hosts that are not denylisted.

    Ported from classify_v2.py:80-90 (v2).
    """

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


def dotted_class(raw):
    """Convert a Dalvik class descriptor to a dotted name.

    Ported from extract_v2.py:67-73 (v2).
    """

    if raw is None:
        return ""
    name = str(raw)
    if name.startswith("L") and name.endswith(";"):
        name = name[1:-1]
    return name.replace("/", ".")


def package_of_class(dotted):
    """Return the package of a dotted class name; keep empty-string default package.

    Ported from extract_v2.py:76-85 (v2).
    """

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
    """Assign one Java package to a v2 category.

    Ported from classify_v2.py:105-141 (v2).
    """

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


def classify_cached(package, app_id, catalog, cache):
    """Cache classify_package, dropping the first-party rule element.

    Ported from aggregate_v2.py:78-85 (v2).
    """

    key = (package or "", app_id or "")
    hit = cache.get(key)
    if hit is None:
        cat, sdk_name, sdk_cat, fw, _rule = classify_package(package, app_id, catalog, cfg)
        hit = (cat, sdk_name, sdk_cat, fw)
        cache[key] = hit
    return hit


def classify_packages(packages: list[str], application_id: str) -> dict[str, str]:
    """Map package names to category labels using the frozen catalog."""

    catalog = load_catalog()
    cache = {}
    out = {}
    for pkg in packages:
        cat, _sdk_name, _sdk_cat, _fw = classify_cached(pkg, application_id, catalog, cache)
        out[pkg] = cat
    return out
