# Reference data provenance

Port date: 2026-10-29

extract_v2.py, aggregate_v2.py and manifest_v2b.py were not covered by the 24 Oct 2026 freeze manifest; hashes here were recorded at port time.

## Environment

- Python: 3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]
- androguard: 3.3.5
- pydantic: 2.14.1
- OS: Windows-11-10.0.26300-SP0

## Vendored into `data/reference/` (byte-identical copies)

| File | Source path on E:\ | SHA256 | Date copied | in 24 Oct freeze manifest | decision_log |
| --- | --- | --- | --- | --- | --- |
| `sdk_catalog.csv` | `E:\AndroZoo\analyzer\pipeline_v2\sdk_catalog.csv` | `1327e3e6d92988fe1c2daa7c13badb9a32c0cfef4288899a4fff720aa28e5c10` | 2026-10-29 | yes | D-020 |
| `config_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\config_v2.py` | `51e9ebae848b07c14e19e8cef675081f66fd1b7ef6718ddd383ea2ceafc6664a` | 2026-10-29 | yes | D-020 |
| `classify_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\classify_v2.py` | `56d025ec08db0e976ac031b83271bd3cf341fcf2dbf05097026a64b576eba52d` | 2026-10-29 | yes | D-020 |

`validation_key.csv` and `validation_blind.csv` were not vendored.

## Port sources (not all freeze-listed)

| File | Source path on E:\ | SHA256 (port time) | Port date | in 24 Oct freeze manifest | decision_log |
| --- | --- | --- | --- | --- | --- |
| `extract_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py` | `f8a2933b32e1d50a999769e3400fe9e9aaac593dd82d0058cf01d14247901fcc` | 2026-10-29 | no | D-009 |
| `aggregate_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py` | `097cb9ed5cbd7cf2aa3368a0bbd8e16f7b9fbb2ff9a6443415f96e1056ec4a16` | 2026-10-29 | no | D-009, D-011, D-013 |
| `manifest_v2b.py` | `E:\AndroZoo\analyzer\pipeline_v2\manifest_v2b.py` | `a06962166eb7c3900b6355a08dd8ff4eaff2c8f6df8f1a26020b876f47fbed03` | 2026-10-29 | no | D-014, D-015 |
| `classify_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\classify_v2.py` | `56d025ec08db0e976ac031b83271bd3cf341fcf2dbf05097026a64b576eba52d` | 2026-10-29 | yes | D-020 |
| `config_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\config_v2.py` | `51e9ebae848b07c14e19e8cef675081f66fd1b7ef6718ddd383ea2ceafc6664a` | 2026-10-29 | yes | D-020 |
| `test_classify.py` | `E:\AndroZoo\analyzer\pipeline_v2\test_classify.py` | `6d1303897b8d497bd7a3299dabc45857fc8c930285b3fb40953dd3414c0b8e14` | 2026-10-29 | no | D-020 |
| `sdk_catalog.csv` | `E:\AndroZoo\analyzer\pipeline_v2\sdk_catalog.csv` | `1327e3e6d92988fe1c2daa7c13badb9a32c0cfef4288899a4fff720aa28e5c10` | 2026-10-29 | yes | D-020 |

## Parity validation (Phase 1B)

Date: 2026-10-29

Population rule: `apk_level` rows whose sha256 has `included=True` in `analytic_sample.csv`, minus every sha256 in `validation_blind.csv`. Stratum = `apk_level.stratum`. `random.Random(42).sample` of 2 per stratum, strata in sorted order (30 APKs). Paths: `E:\AndroZoo\apks\<SHA256 uppercase>.apk`.

Seed: 42. n=30 (2 per stratum, validation set excluded).

Compared columns (35): min_sdk, target_sdk, n_dex_files, total_dex_bytes, classes_dex_bytes, n_classes, n_methods_defined, n_native_libs, frameworks_detected, n_packages_total, n_packages_toolchain, n_packages_framework, n_packages_sdk, n_packages_first_party, n_packages_obfuscated, n_packages_unattributed_third_party, footprint_strict_pct, footprint_inclusive_pct, footprint_strict_nontoolchain_pct, footprint_service_pct, n_sdk_distinct, hosts_distinct_all, hosts_distinct_sdk, hosts_distinct_first_party, n_urls_unparseable, debuggable_explicit, allowBackup_explicit, usesCleartextTraffic_explicit, networkSecurityConfig, nsc_parsed, nsc_error, nsc_cleartextTrafficPermitted_true, nsc_resolve_call, ns_fallback_manifest_count, n_call_rows

Result: 35/35 columns matched on 30/30 APKs.

Normalisation rule (from `aggregate_v2.py:369` `pd.DataFrame.to_csv`, not `csv.DictWriter`):
- `None` / empty CSV cell ↔ `""`
- booleans as pandas writes them: `True` / `False`
- `footprint_*` floats compared after `round(..., 6)`
- `frameworks_detected` as `";".join` of names in `FRAMEWORK_PREFIXES` insertion order (`join_fw`)
- integer-valued numeric cells that pandas wrote as `"47.0"` because the column mixed with `None` (`ns_fallback_manifest_count`) compared as int strings

androguard 3.3.5 / Python 3.12.10 on both sides.

## Known v2 defects (not fixed)

- D9: overlay `nsc_error` is not copied into `obj["errors"]`, so `apk_level` and `errors_long` disagree (78 vs 77).
- Two `is_ip_literal` copies: extract_v2:88–94 has no `(host or "")`; classify_v2:63–69 does.
- extract_v2 `android_attr` is namespaced-only; v2b adds non-namespaced fallback (D-014). That is why D9’s extract JSON missed the NSC ref.
- `nsc_attr` tries un-namespaced first; `android_attr` tries namespaced first.
- `aggregate_v2.py` discards `frameworks_detected` evidence (`_fw_ev`).
- `ns_fallback_manifest_count` is written as floats (`0.0`, `47.0`, …) because pandas mixed `None` with ints.
