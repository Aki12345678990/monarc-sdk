"""P indicator.

This module will compute the P indicator from manifest permission names. The
computation must be ported byte-faithfully from the frozen v2 pipeline. No
logic may be added before that port.
"""


def compute_P(manifest_permissions: list[str]) -> dict:
    raise NotImplementedError("Awaiting Phase 1B port from frozen v2 pipeline")
