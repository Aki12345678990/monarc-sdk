"""Framework detection.

This module will report cross-platform frameworks present in an APK from its
file list and Java package names. The computation must be ported
byte-faithfully from the frozen v2 pipeline. No logic may be added before
that port.
"""


def detect_frameworks(apk_file_list: list[str], packages: list[str]) -> list[dict]:
    raise NotImplementedError("Awaiting Phase 1B port from frozen v2 pipeline")
