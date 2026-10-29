"""Framework detection. Ported from classify_v2.py (v2)."""

from analyzer_core import v2_constants as cfg


def frameworks_detected(packages, native_libs, cfg):
    """Return detected framework names and evidence strings.

    Ported from classify_v2.py:144-167 (v2).
    """

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


def detect_frameworks(apk_file_list: list[str], packages: list[str]) -> list[dict]:
    """Wrapper kept for the Phase 1A stub signature; uses package names only.

    Native-lib evidence requires basenames collected like extract_v2.py:243-249.
    Call ``frameworks_detected`` from the isolated child for the full v2 result.
    """

    native_libs = []
    for name in apk_file_list or []:
        parts = str(name).replace("\\", "/").split("/")
        if len(parts) == 3 and parts[0] == "lib" and parts[2].endswith(".so"):
            native_libs.append(parts[2])
    detected, ev_out = frameworks_detected(packages, native_libs, cfg)
    return [{"name": name, "evidence": ev_out[name]} for name in detected]
