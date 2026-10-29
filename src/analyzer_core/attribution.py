"""Package attribution.

This module will map each Java package name to an attribution label for one
application id. The computation must be ported byte-faithfully from the frozen
v2 pipeline. No logic may be added before that port.
"""


def classify_packages(packages: list[str], application_id: str) -> dict[str, str]:
    raise NotImplementedError("Awaiting Phase 1B port from frozen v2 pipeline")
