"""N indicator.

N is the paper definition: distinct hosts in SDK-attributed code, from
indicators_v2.py compute_n (accept_host, extension denylist, frozen classifier).

N_all is the same host filter over every caller. The extract's hosts_distinct_all
is retained as a separate fact and is not N_all.
"""

from analyzer_core.indicators.v2_rules import compute_n, psl_and_extension


def compute_N(*, host_recs, app_id, catalog, hosts_distinct_all: int) -> dict:
    """Return paper N, with paper N_all and the unchanged extract host count."""

    psl, extension = psl_and_extension()
    result = compute_n(host_recs or [], app_id, catalog, {}, psl, extension)
    return {
        "status": "ok",
        "value": result["N"],
        "reason": None,
        "definition_source": "indicators_v2.py:compute_n",
        "details": {
            "N_all": result["N_all"],
            "hosts_distinct_all": hosts_distinct_all,
            "hosts": result["hosts"],
        },
    }
