"""A indicator.

This module will compute the A indicator from the DEX analysis object and the
package attribution map. The computation must be ported byte-faithfully from
the frozen v2 pipeline. No logic may be added before that port.
"""


def compute_A(dx, attribution: dict[str, str]) -> dict:
    raise NotImplementedError("Awaiting Phase 1B port from frozen v2 pipeline")
