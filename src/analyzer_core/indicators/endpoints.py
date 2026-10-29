"""N indicator.

Ported from extract_v2.py:272-304 and aggregate_v2.py:201-225 (v2).
"""


def compute_N(
    *,
    hosts_distinct_all: int,
    hosts_distinct_sdk: int,
    hosts_distinct_first_party: int,
    n_urls_unparseable: int | None,
    hosts: list[dict],
) -> dict:
    """Return N as hosts_distinct_all after HOST_DENYLIST filtering.

    Ported from extract_v2.py:272-304, aggregate_v2.py:201-225 (v2).
    """

    return {
        "status": "ok",
        "value": hosts_distinct_all,
        "reason": None,
        "definition_source": "extract_v2.py:272-304, aggregate_v2.py:201-225",
        "details": {
            "hosts_distinct_all": hosts_distinct_all,
            "hosts_distinct_sdk": hosts_distinct_sdk,
            "hosts_distinct_first_party": hosts_distinct_first_party,
            "n_urls_unparseable": n_urls_unparseable,
            "hosts": hosts,
        },
    }
