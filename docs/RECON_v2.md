# Phase B0 — v2 pipeline recon

Date: 2026-10-29

Read-only recon of `E:\AndroZoo\analyzer\`. Nothing under `E:\` was created, modified, moved, renamed, or deleted. No research script was executed (`extract_v2.py`, `run_extract_v2.py`, `aggregate_v2.py`, `run_all.py`, v1 scripts 01–05). No `.lock` file was touched. No secret was printed. Validation-set rows and per-package attribution labels for validation-set APKs were not printed. `docs\RECON.md` was not edited. Phase B1 was not started.

---

## Critical — freeze SHA256

No CRITICAL mismatch. Every file listed in the freeze manifest was re-hashed; all four are **MATCH**.

| Freeze key | Path | Expected (manifest) | Actual (recomputed) | Result |
| --- | --- | --- | --- | --- |
| `sdk_catalog_csv_sha256` | `E:\AndroZoo\analyzer\pipeline_v2\sdk_catalog.csv` | `1327e3e6d92988fe1c2daa7c13badb9a32c0cfef4288899a4fff720aa28e5c10` | `1327e3e6d92988fe1c2daa7c13badb9a32c0cfef4288899a4fff720aa28e5c10` | MATCH |
| `config_v2_py_sha256` | `E:\AndroZoo\analyzer\pipeline_v2\config_v2.py` | `51e9ebae848b07c14e19e8cef675081f66fd1b7ef6718ddd383ea2ceafc6664a` | `51e9ebae848b07c14e19e8cef675081f66fd1b7ef6718ddd383ea2ceafc6664a` | MATCH |
| `classify_v2_py_sha256` | `E:\AndroZoo\analyzer\pipeline_v2\classify_v2.py` | `56d025ec08db0e976ac031b83271bd3cf341fcf2dbf05097026a64b576eba52d` | `56d025ec08db0e976ac031b83271bd3cf341fcf2dbf05097026a64b576eba52d` | MATCH |
| `validation_key_sha256` | `E:\AndroZoo\analyzer\results_v2\validation\validation_key.csv` | `265a70d0d81b133de64ee539aaf67ef1846340b33a985796afdbeb820e7cc216` | `265a70d0d81b133de64ee539aaf67ef1846340b33a985796afdbeb820e7cc216` | MATCH |

The freeze manifest does **not** list `extract_v2.py`, `aggregate_v2.py`, `run_extract_v2.py`, `manifest_v2b.py`, or the sensitive-API map.

---

## B0.1 Path check

Specified root: `E:\AndroZoo\analyzer\`

| Check | Result |
| --- | --- |
| `Test-Path E:\AndroZoo\analyzer` | `True` |
| `Test-Path E:\AndroZoo\apks` | `True` |

`E:\AndroZoo\` children: `metadata\`, `apks\`, `scripts\`, `analyzer\`.

---

## B0.2 Artefacts

### a) Every `*_v2.py` file

| File | Absolute path | Size (bytes) | SHA256 |
| --- | --- | --- | --- |
| `extract_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py` | 14296 | `f8a2933b32e1d50a999769e3400fe9e9aaac593dd82d0058cf01d14247901fcc` |
| `classify_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\classify_v2.py` | 5803 | `56d025ec08db0e976ac031b83271bd3cf341fcf2dbf05097026a64b576eba52d` |
| `run_extract_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\run_extract_v2.py` | 6783 | `07eb4ff369f39eac22ce5f1f3f66c6187d6f8e2f4a89b717aaa8b96c62535eeb` |
| `aggregate_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py` | 16457 | `097cb9ed5cbd7cf2aa3368a0bbd8e16f7b9fbb2ff9a6443415f96e1056ec4a16` |
| `config_v2.py` | `E:\AndroZoo\analyzer\pipeline_v2\config_v2.py` | 3226 | `51e9ebae848b07c14e19e8cef675081f66fd1b7ef6718ddd383ea2ceafc6664a` |
| `build_sample_v2.py` | `E:\AndroZoo\analyzer\sampling\build_sample_v2.py` | 10094 | `d1146dd868bc0c53691f52756ce7ede86cf8753db8e6a5e43e4b2db0caae9bcc` |
| `download_v2.py` | `E:\AndroZoo\analyzer\sampling\download_v2.py` | 6740 | `f80081ec6ea0d6738ba1eb7c92ca13d716131912f28c1529a64497816eb8e2e3` |

Related v2 pipeline modules whose names do not match `*_v2.py`:

| File | Absolute path | Size (bytes) | SHA256 |
| --- | --- | --- | --- |
| `manifest_v2b.py` | `E:\AndroZoo\analyzer\pipeline_v2\manifest_v2b.py` | 10364 | `a06962166eb7c3900b6355a08dd8ff4eaff2c8f6df8f1a26020b876f47fbed03` |
| `test_classify.py` | `E:\AndroZoo\analyzer\pipeline_v2\test_classify.py` | 5264 | `6d1303897b8d497bd7a3299dabc45857fc8c930285b3fb40953dd3414c0b8e14` |
| `build_analytic_sample.py` | `E:\AndroZoo\analyzer\pipeline_v2\build_analytic_sample.py` | 7078 | `728f0b423fb13180d14cec68121db100ee6799ade193c4a7316a2cfccee34880` |
| `build_validation_set.py` | `E:\AndroZoo\analyzer\pipeline_v2\build_validation_set.py` | 7205 | `cfba2350383aabfd7b4d9a6da57e2efbb2b22787c729f845b72866023b46e64d` |

### b) Frozen SDK catalog

- Path: `E:\AndroZoo\analyzer\pipeline_v2\sdk_catalog.csv`
- Size: 36965 bytes
- SHA256: `1327e3e6d92988fe1c2daa7c13badb9a32c0cfef4288899a4fff720aa28e5c10` (MATCH freeze)
- Raw line count: 486 (1 comment + 1 header + 484 data)
- Data rows (comment/blank lines skipped, same rule as `classify_v2.load_catalog`): **484** (matches `catalog_freeze.json` `catalog_row_count`)
- Line 1 (comment, not a data row): `# allowed_categories: ads,analytics,attribution,crash_reporting,social,networking,payments,maps_location,push_messaging,ui,game_engine,cloud_backend,utility,uncertain,media,framework_plugin`
- Header: `prefix,sdk_name,category,source,match_type`
- Rows per `source` (from freeze): `v1_config` 59, `v2_added` 1, `v2_curation_round2` 116, `v2_curation_round3` 234, `v2_curation_round3b` 12, `v2_pilot_curation` 62

### c) Freeze manifest

- Path: `E:\AndroZoo\analyzer\docs\catalog_freeze.json`
- Size: 793 bytes
- SHA256: `15647730a39ca4ca23c154183eec2c28357753967b8feb877cb62a0b67ff807a`
- `freeze_timestamp_iso`: `2026-10-24T15:35:09.491276+00:00`
- Statement: `Frozen before any association between SDK footprint and outcome indicators was computed.`
- Listed files and MATCH/MISMATCH: see Critical section. All MATCH.

### d) Files whose name contains `sensitive_api_map`

Only one file:

- Path: `E:\AndroZoo\analyzer\pipeline_v2\sensitive_api_map_SEED_TEST.csv`
- Size: 1139 bytes
- SHA256: `e0a483d5acff2d5825f0948ab917be5e482406ebad440dae6ddca00147cbedae`
- Header: `class,method,permissions,source`
- Data rows: **12**
- `source` column: all 12 rows are `TEST_SEED_NOT_FOR_RESULTS`

Which file `aggregate_v2.py` / config points at:

- `config_v2.py:14`: `SENSITIVE_API_MAP_CSV = os.path.join(PIPELINE_DIR, "sensitive_api_map_SEED_TEST.csv")`
- `aggregate_v2.py:104-107`: `--api-map` default is `cfg.SENSITIVE_API_MAP_CSV`
- `apk_level.csv` column `api_map_filename`: `sensitive_api_map_SEED_TEST.csv` on 1709 rows; empty on 1 row (the AnalyzeAPK failure)

There is no API 28–33 finalised map in this tree. This is a SEED/TEST file.

### e) Dangerous-permission list used for P

**v2 does not compute P and does not reference a dangerous-permission list.**

- `extract_v2.py:225` stores `permissions_requested = list(a.get_permissions())` in per-APK raw JSON.
- `aggregate_v2.py` never reads `permissions_requested`.
- `apk_level.csv` has no permission-count column and no `P` column.

The only dangerous-permission list in the analyzer tree is a **v1** in-code constant, not used by any `*_v2.py`:

- Location: `E:\AndroZoo\analyzer\config.py` lines 56–102, name `DANGEROUS_PERMISSIONS` (a `set` of 39 strings)
- File SHA256: `81363b57b1e284ecbb23371c5a697eae673cb5706dbabf56efc34cd9a15a5134` (8384 bytes)
- Consumer: v1 `02_extract_metrics.py:31-35` (`declared_perms & DANGEROUS_PERMISSIONS`). That script is v1 (HARD CONSTRAINT 2: not executed).

### f) Framework detection logic location

- Prefix and native-lib tables: `E:\AndroZoo\analyzer\pipeline_v2\config_v2.py` lines 42–75 (`FRAMEWORK_PREFIXES`, `FRAMEWORK_NATIVE_LIBS`)
- Detection function: `E:\AndroZoo\analyzer\pipeline_v2\classify_v2.py` lines 144–167 (`frameworks_detected`)
- Call site: `aggregate_v2.py:199` (`frameworks_detected(list(packages.keys()), native_libs, cfg)`)
- Classifier also short-circuits packages into category `"framework"` in `classify_package` lines 111–119, using the same `FRAMEWORK_PREFIXES`

### g) Manual attribution validation-set file

Rows are not printed.

Blind set (validator-facing):

- Path: `E:\AndroZoo\analyzer\results_v2\validation\validation_blind.csv`
- Size: 76389 bytes
- SHA256: `de6de93758168d49d4e3e7aaae4f4f440da34e717d22041ce0e4cf92b4dfe96a`
- Data rows: **200**
- Unique `sha256` count: **20** (not listed)
- Header: `item_id,sha256,applicationId,apk_path,package,n_classes_in_package,example_classes,human_label,human_sdk_name,human_notes`

Key (pipeline labels; hashed in freeze):

- Path: `E:\AndroZoo\analyzer\results_v2\validation\validation_key.csv`
- Size: 6055 bytes
- SHA256: `265a70d0d81b133de64ee539aaf67ef1846340b33a985796afdbeb820e7cc216` (MATCH freeze)
- Data rows: **200**
- Header: `item_id,category,sdk_name,sdk_category,framework_name`

Construction: `pipeline_v2\build_validation_set.py` (D-021: 20 APKs, seed 42, 10 non-toolchain packages per APK).

### h) `docs\decision_log.md`

- Path: `E:\AndroZoo\analyzer\docs\decision_log.md`
- Size: 10387 bytes
- SHA256: `3fd29c1c0491bb70567c84305231600da0631253e068dff11795e093653f35b6`
- Highest D-number: **D-022**
- Entry titles only:

  - D-001 Sampling date field
  - D-002 Malware-labelled apps removed
  - D-003 Stratification variable
  - D-004 Deduplication
  - D-005 White-label cluster robustness check (declared before analysis)
  - D-006 Download integrity
  - D-007 dex_size saturation (hypothesis, pending verification)
  - D-007 verification
  - D-008 Cross-platform frameworks
  - D-009 Raw-first extraction
  - D-010 SDK catalog curation from pilot
  - D-011 Secondary footprint measures
  - D-012 Catalog curation round 2
  - D-013 Catalog curation stopping rule (declared before full-sample aggregation)
  - D-014 Manifest attribute namespace fallback
  - D-014 amendment
  - D-015 Unresolvable network security configs
  - D-016 Inclusion criterion operationalisation
  - D-017 Parse failure replacement
  - D-018 Catalog curation round 3
  - D-019 Analytic sample construction
  - D-020 Catalog curation round 3b and freeze
  - D-021 Blinded attribution validation
  - D-022 Debug tooling presence (descriptive only)

ROOT has no `docs\decision_log.md`.

### i) v2 test files and test names

v2 classifier tests (not pytest; a `main()` of `assert`s):

- Path: `E:\AndroZoo\analyzer\pipeline_v2\test_classify.py`
- Top-level functions: `main` only
- No `test_*` function names. Asserts inside `main()` (executed only if the file is run; it was **not** run):

  1. `kotlin` → category `toolchain`
  2. `kotlin.collections` → `toolchain`
  3. `com.google.android.material` → `toolchain`
  4. `com.foobar` is not SDK name `Foo` (prefix-boundary)
  5. `com.facebook.react.bridge` → `framework` / `react_native`
  6. `com.unity3d.player` → `framework` / `unity`
  7. `com.unity3d.ads` → `sdk` (not `framework`)
  8. `host_ok("www.")` is False
  9. `host_ok("example.com")` is False (denylist)
  10. `host_ok("foo.example.com")` is False (denylist suffix)
  11. `host_ok("schemas.microsoft.com")` is False
  12. `host_ok("github.com")` is True, not IP
  13. `host_ok("8.8.8.8")` is True, IP
  14. `host_denied("page.example.org")` is True
  15. `com.facebook` → SDK `Facebook SDK`
  16. `com.facebook.login.widget` → `Facebook SDK`
  17. `com.facebook.soloader` → `Meta OSS libraries`
  18. `com.facebook.fbreact.specs` → `framework` / `react_native`
  19. `com.google.errorprone.annotations` → `toolchain`
  20. `bitter.jnibridge` → `framework` / `unity`
  21. `org.fmod` → `framework` / `unity`
  22. `com.facebook.katana.feed` with app id `com.facebook.katana` → `first_party` rule `exact`
  23. `com.facebook.login` with that app id → `Facebook SDK` (SDK before leftover first-party)
  24. `com.google.android.gms.internal.ads` → `Google Mobile Ads` / `ads`
  25. `com.google.android.gms.internal.mlkit_vision_digital_ink` → `ML Kit`
  26. `com.google.android.gms.foo` → `Google Play Services (other)`
  27. `com.google.android.a` → `Google (unresolved)` (asserted twice)
  28. `com.facebook.k.n` → `Meta (unresolved)`
  29. `com.facebook.imagepipeline.core` → `Fresco`
  30. `com.facebook.debug.holder` → `framework` / `react_native`
  31. `_COROUTINE` → `toolchain`
  32. `com.squareup.picasso` → `Picasso`
  33. `org.junit.runner` → `toolchain`
  34. `j$.time` → `toolchain`
  35. `com.xamarin.forms.platform.android` → `framework` / `xamarin_maui`
  36. `org.cocos2dx.lib` → `framework` / `cocos2dx`
  37. `com.google.android.gms.identity.intents.model` → `Google Pay`
  38. `com.google.android.gms.identity` → `Google Play Services Auth`
  39. `com.google.android.gms.tagmanager_legacy` → `Google Tag Manager`
  40. `com.bytedance.sdk.component.g` → `Pangle`
  41. `com.bytedance` → `ByteDance (unresolved)`
  42. `com.amazon.device.ads` → `Amazon Publisher Services`
  43. `expo.modules.core` → `Expo modules`
  44. `com.microsoft.appcenter.crashes` → `App Center Crashes` / `crash_reporting`
  45. `net.sqlcipher.database` → `SQLCipher`
  46. `com.unity3d.mediation.banner` → `Unity LevelPlay Mediation`
  47. `com.amazon.a.a.b` → `Amazon (unresolved)`
  48. `validate_catalog()` succeeds on the frozen catalog

Not a v2 indicator test (legacy download smoke test; not executed): `E:\AndroZoo\analyzer\sampling\legacy\test_download.py`. It reads AndroZoo credentials from the environment. No `test_*` functions.

`E:\AndroZoo\analyzer\venv\` contains third-party package tests; those are not v2 tests.

### j) v2 per-APK results tables (header and row count only)

| Path | Size | SHA256 | Data rows | Header |
| --- | --- | --- | --- | --- |
| `E:\AndroZoo\analyzer\results_v2\apk_level.csv` | 955182 | `e90c4a206a6748decef335ec071a5c117c825aed0aadc36ee09e6de794a040cc` | 1710 | `sha256,package,min_sdk,target_sdk,total_dex_bytes,classes_dex_bytes,n_classes,n_methods_defined,n_packages_total,n_packages_framework,footprint_strict_pct,footprint_inclusive_pct,footprint_strict_nontoolchain_pct,footprint_service_pct,n_sdk_distinct,api_hits_total,api_hits_sdk,api_distinct_overall,api_distinct_sdk,hosts_distinct_all,hosts_distinct_sdk,hosts_distinct_first_party,debuggable_explicit,allowBackup_explicit,usesCleartextTraffic_explicit,networkSecurityConfig,nsc_parsed,nsc_error,nsc_cleartextTrafficPermitted_true,nsc_resolve_call,n_urls_unparseable,n_call_rows,elapsed_seconds,python_version,androguard_version,api_map_filename,n_errors,frameworks_detected,n_native_libs,n_dex_files,ns_fallback_manifest_count,n_packages_toolchain,api_hits_toolchain,api_distinct_toolchain,api_hits_framework,api_distinct_framework,n_packages_sdk,n_packages_first_party,api_hits_first_party,api_distinct_first_party,n_packages_obfuscated,api_hits_obfuscated,api_distinct_obfuscated,n_packages_unattributed_third_party,api_hits_unattributed_third_party,api_distinct_unattributed_third_party,stratum,year,size_q,apk_size,dex_size,role,draw_rank` |
| `E:\AndroZoo\analyzer\results_v2\extract_run_log.csv` | 310844 | `f5bd47a3479098ef97a1fbbf9895d7042fb613f7937d486f701ba93066a92580` | 2311 | `sha256,role,stratum,status,elapsed_s,timestamp_iso` |
| `E:\AndroZoo\analyzer\results_v2\analytic_sample.csv` | 164302 | `2102eeb6f79d6e479880d652dff2190f7f0abe1f0d1776d5558a17dcbe87580d` | 1710 | `sha256,stratum,role,draw_rank,included,exclusion_reason` |
| `E:\AndroZoo\analyzer\results_v2\analytic_sample_D019.csv` | 164302 | `2102eeb6f79d6e479880d652dff2190f7f0abe1f0d1776d5558a17dcbe87580d` | 1710 | same as `analytic_sample.csv` (byte-identical) |
| `E:\AndroZoo\analyzer\results_v2\sdk_packages_long.csv` | 51055879 | `b3c45d823fedf4ac51bfdabd73c0debd1b10f80ab0aa8a64283dc0f873acea35` | 406216 | `sha256,package,sdk_name,sdk_category,n_classes` |
| `E:\AndroZoo\analyzer\results_v2\api_hits_long.csv` | 1554087 | `484ad3227342767ba45c4f6303259e2932a1ad4cde34b8157dae28af527ad46d` | 8445 | `sha256,caller_package,caller_attribution,caller_sdk_name,api_class,api_method,permissions,n_callsites` |
| `E:\AndroZoo\analyzer\results_v2\hosts_long.csv` | 8356448 | `2487d2b2d6b8bde6e8dbfea81e69a42e471a55fdd4f8981d7f3dc514ca9ff410` | 59628 | `sha256,host,caller_package,attribution,sdk_name,ip_literal` |
| `E:\AndroZoo\analyzer\results_v2\components_long.csv` | 17041014 | `fd869c257713bbd953192d1b2c90209e959aa9b6d9c9ca0846c1741c8a9328e3` | 81033 | `sha256,type,name,exported_explicit,has_intent_filter,permission,readPermission,writePermission,is_launcher,attribution,sdk_name,component_package,sdk_category,framework_name` |
| `E:\AndroZoo\analyzer\results_v2\errors_long.csv` | 9516 | `9aae2dc0a49ed1899de7e7948cb8d9c8bd9517637568137257d0f5d30fd995f9` | 78 | `sha256,section,exception,message` |
| `E:\AndroZoo\analyzer\results_v2\unattributed_roots.csv` | 1002639 | `538f0e85c058e706bbdc8189d82971c0b3475e99a6ae53c138fba158832feda7` | 24593 | `root,n_apks_containing,total_classes,example_packages` |
| `E:\AndroZoo\analyzer\results_v2\package_assignments.csv` | 7474440 | `795fe2b8aaff317090db572b98328136da4685d7e9992094b26e0983d7934a01` | 135902 | `package,category,sdk_name,sdk_category,framework_name,n_apks` |

Pilot/pretest logs (not the full-sample table): `extract_run_log_pilot1.csv` (60 rows), `extract_run_log_pretest.csv` (3 rows). Same header as `extract_run_log.csv`.

Raw per-APK artefacts (not tables): `results_v2\raw\` 1709 `*.json` + 1 `*.error.json`; `results_v2\raw_calls\` 1709 `*.csv.gz`; `results_v2\raw_manifest\` 1709 `*.json`. `consort_flow.json` records D-019 inclusion flow (`final_n` 1260).

### k) APK folder

- Path: `E:\AndroZoo\apks` (`config_v2.py:4` `APK_DIR`)
- Number of `.apk` files: **3710**
- Other files in that folder: 0
- Naming: `{SHA256}.apk` (uppercase SHA256 in v2 extract)
- Sample size is 1710; the extra APKs on disk are outside the v2 sample (v1 leftovers or otherwise). Cannot determine the extra 2000 without a broader inventory that this prompt does not request.

### l) v2 sample/selection file (strata and status ok/error)

No single draw file contains both the sample-design columns (`draw_rank`, `role`, `year`, `size_q`) and extract `ok`/`error`.

**Draw / strata (no extract status):**

- Path: `E:\AndroZoo\metadata\sample_v2.csv` (`config_v2.py:6` `SAMPLE_CSV`)
- Size: 342083 bytes
- SHA256: `19e0b7263ebcf3660e03ae9af2244b8c0064c0f41d59ffba82225b2fa6b678de`
- Data rows: 1710
- Header: `sha256,pkg_name,vercode,vt_detection,vt_scan_date,added,apk_size,dex_size,year,size_q,stratum,draw_rank,role,already_on_disk`
- Strata (15): `2022_Q1` … `2022_Q5`, `2023_Q1` … `2023_Q5`, `2024_Q1` … `2024_Q5`
- Role counts: primary 1260, reserve 450
- `already_on_disk`: all `False` (column is the pre-download flag from `build_sample_v2.py`, not current disk state)

**Extract status + stratum (duplicate rows from re-runs):**

- Path: `E:\AndroZoo\analyzer\results_v2\extract_run_log.csv`
- Header includes `stratum` and `status`
- 2311 rows for 1710 unique SHA256
- Row-level status counts: `ok` 1710, `skipped_done` 600, `error` 1
- Unique SHA256 with at least one `ok`: **1709**
- Unique SHA256 with `error` and no `ok`: **1**

**Analytic inclusion (D-016/D-019, not extract status):**

- `analytic_sample.csv`: `included` True 1260, False 450
- `exclusion_reason`: empty 1260 (included), `lt2_sdk_namespaces` 63, `reserve_not_needed` 386, `parse_failure` 1

**Download log** (HTTP status, not extract status): `E:\AndroZoo\metadata\download_v2_log.csv`, 1716 rows, header `sha256,role,stratum,draw_rank,status,http_status,bytes,attempts,error,timestamp_iso`, status `ok` 1710 / `skipped_verified` 6.

B1.6 names four args: per-APK results table, APK folder, sample file, validation-set file. The sample-file path that defines strata is `sample_v2.csv`. The ok/error field lives on `extract_run_log.csv`. Which file B1.6 should receive as “v2 sample file” is not decided here.

---

## B0.3 Function inventory (`extract_v2.py`, `classify_v2.py`)

Modules were **not imported** (HARD CONSTRAINT 2). Import-time behaviour is from AST + source.

### `extract_v2.py` — imports without running `extract_one` / `main`

Yes, provided `config_v2` is importable. Top-level: stdlib imports; `sys.path.insert(0, pipeline_v2 dir)` at line 13; `from config_v2 import ANDROID_NS, APK_DIR, RAW_CALLS_DIR, RAW_DIR` at line 14; compile `URL_RE` / `HOST_RE`; define constants and functions; `if __name__ == "__main__": main()` at lines 403–404. `config_v2` is constants only (no `makedirs`). Import-time side effect: `sys.path` mutation. No file writes unless `main`/`extract_one`/`ensure_dirs` are called.

Hardcoded / config paths:

- Line 13: `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`
- Line 14: `APK_DIR`, `RAW_CALLS_DIR`, `RAW_DIR` from `config_v2`
- Line 176: `os.path.join(APK_DIR, sha256 + ".apk")`
- Line 213: `os.path.join(RAW_DIR, sha256 + ".error.json")`
- Line 384: `os.path.join(RAW_CALLS_DIR, sha256 + ".csv.gz")`
- Line 389: `os.path.join(RAW_DIR, sha256 + ".json")`
- `config_v2.py:3`: `ROOT = os.environ.get("ANDROZOO_ROOT", r"E:\AndroZoo")`
- `config_v2.py:4-10`: `APK_DIR`, `SAMPLE_CSV`, `RESULTS_V2`, `RAW_DIR`, `RAW_CALLS_DIR`, `EXTRACT_LOG`

| Name | Signature | Lines | Purpose | Side effects |
| --- | --- | --- | --- | --- |
| `ensure_dirs` | `()` | 24–26 | Create raw output directories | `os.makedirs` on `RAW_DIR`, `RAW_CALLS_DIR` |
| `write_json_atomic` | `(path, obj)` | 29–34 | Atomic JSON write | writes `path+".tmp"` then `os.replace` to `path` |
| `write_calls_atomic` | `(path, rows)` | 37–47 | Atomic gzip CSV of call rows | writes `path+".tmp"` gzip then replace |
| `record_error` | `(errors, section, exc)` | 50–55 | Append exception record | mutates `errors` list |
| `to_int_or_none` | `(val)` | 58–64 | Parse int or None | none |
| `dotted_class` | `(raw)` | 67–73 | `Lfoo/bar;` → `foo.bar` | none |
| `package_of_class` | `(dotted)` | 76–85 | Class name → package; strips `$` inner-class suffix | none |
| `is_ip_literal` | `(host)` | 88–94 | IPv4/IPv6 literal check | none |
| `host_keep` | `(host)` | 97–105 | Keep IP or DNS-looking host; **no denylist** | none |
| `android_attr` | `(elem, name)` | 108–109 | Read `{ANDROID_NS}name` only | none |
| `resolve_component_name` | `(raw, application_id)` | 112–118 | Resolve `.Foo` against application id | none |
| `parse_nsc_cleartext` | `(root)` | 121–131 | True iff any NSC `base-config`/`domain-config` has `cleartextTrafficPermitted="true"` | none |
| `resolve_nsc_path` | `(a, ref)` | 134–165 | Resolve `@xml/` via zip names or `@0x…` via ARSC | reads APK zip / ARSC; no disk write |
| `extract_one` | `(sha256)` | 168–392 | Parse one APK; fill `out`; write raw JSON and calls | file writes listed above; reads APK under `APK_DIR` |
| `main` | `()` | 395–400 | CLI `--sha` | `ensure_dirs()`; `extract_one`; `sys.exit` |

### `classify_v2.py` — imports without running classification

Yes, provided `config_v2` is importable. No `if __name__` guard and no `main`. Top-level: imports; `from config_v2 import HOST_DENYLIST, SDK_CATALOG_CSV, SDK_CATEGORY_VOCABULARY`; compile `HOST_RE`; define functions. `load_catalog` is not called at import. No file I/O at import.

Hardcoded / config paths:

- Line 6: `SDK_CATALOG_CSV` (default `pipeline_v2\sdk_catalog.csv`)
- Lines 13–18: `open(path)` when `load_catalog` is called

| Name | Signature | Lines | Purpose | Side effects |
| --- | --- | --- | --- | --- |
| `load_catalog` | `(path=None)` | 13–28 | Load catalog rows; skip `#` comments and blanks | reads CSV from `path` or `SDK_CATALOG_CSV` |
| `validate_catalog` | `(catalog=None, cfg=None)` | 31–60 | Prefix/exact/duplicate/vocabulary checks | may call `load_catalog()`; raises `ValueError` |
| `is_ip_literal` | `(host)` | 63–69 | IPv4/IPv6 literal check | none |
| `host_denied` | `(host)` | 72–77 | HOST_DENYLIST exact or suffix match | none |
| `host_ok` | `(host)` | 80–90 | Keep IP or DNS host **after** denylist | none |
| `package_of_class` | `(dotted)` | 93–102 | Same as extract’s helper | none |
| `classify_package` | `(package, app_id, catalog, cfg)` | 105–141 | One package → `(category, sdk_name, sdk_category, framework_name, first_party_rule)` | none |
| `frameworks_detected` | `(packages, native_libs, cfg)` | 144–167 | Framework names plus evidence strings | none |

---

## B0.4 Exact v2 indicator code

No indicator definition was invented. Where v2 has no implementation, that is stated.

### P — dangerous permissions

**Not implemented in v2.** Collection only:

```221:225:E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py
    try:
        out["package"] = a.get_package()
        out["min_sdk"] = to_int_or_none(a.get_min_sdk_version())
        out["target_sdk"] = to_int_or_none(a.get_target_sdk_version())
        out["permissions_requested"] = list(a.get_permissions())
```

`aggregate_v2.py` does not read this field. No intersection with a dangerous list exists in v2.

The v1 constant (not referenced by v2) at `E:\AndroZoo\analyzer\config.py:56-102`:

```56:102:E:\AndroZoo\analyzer\config.py
DANGEROUS_PERMISSIONS = {
    # Location
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    # Storage
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.MANAGE_EXTERNAL_STORAGE",
    # Camera
    "android.permission.CAMERA",
    # Microphone
    "android.permission.RECORD_AUDIO",
    # Contacts
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.GET_ACCOUNTS",
    # Phone
    "android.permission.READ_PHONE_STATE",
    "android.permission.READ_PHONE_NUMBERS",
    "android.permission.CALL_PHONE",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.ADD_VOICEMAIL",
    "android.permission.USE_SIP",
    "android.permission.PROCESS_OUTGOING_CALLS",
    # SMS
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_WAP_PUSH",
    "android.permission.RECEIVE_MMS",
    # Calendar
    "android.permission.READ_CALENDAR",
    "android.permission.WRITE_CALENDAR",
    # Sensors
    "android.permission.BODY_SENSORS",
    "android.permission.BODY_SENSORS_BACKGROUND",
    # Activity Recognition
    "android.permission.ACTIVITY_RECOGNITION",
    # Bluetooth (API 31+)
    "android.permission.BLUETOOTH_SCAN",
    "android.permission.BLUETOOTH_CONNECT",
    "android.permission.BLUETOOTH_ADVERTISE",
    # Nearby Wifi
    "android.permission.NEARBY_WIFI_DEVICES",
}
```

v1 usage (`02_extract_metrics.py:31-35`), not v2:

```31:35:E:\AndroZoo\analyzer\02_extract_metrics.py
        declared_perms = set(a.get_permissions())
        dangerous_perms = declared_perms & DANGEROUS_PERMISSIONS
        P_count = len(dangerous_perms)
        P_list  = "|".join(sorted(dangerous_perms))
```

### A — sensitive API invocations

**Not restricted to SDK-attributed namespaces at lookup.** Every caller package is classified; hits are counted for all categories and separately for `cat == "sdk"`. The map is the 12-row SEED file.

Extract stores all `android.*` xrefs (not map-filtered):

```363:384:E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py
    try:
        call_counts = defaultdict(int)
        for ma in dx.get_methods():
            if ma.is_external():
                continue
            caller_pkg = package_of_class(dotted_class(ma.get_method().get_class_name()))
            for _ca, target, _off in ma.get_xref_to():
                tclass = dotted_class(target.get_class_name())
                if not tclass.startswith("android."):
                    continue
                call_counts[(caller_pkg, tclass, target.get_name())] += 1
        call_rows = [
            {
                "caller_package": k[0],
                "target_class": k[1],
                "target_method": k[2],
                "n_callsites": n,
            }
            for k, n in sorted(call_counts.items())
        ]
        out["n_call_rows"] = len(call_rows)
        write_calls_atomic(os.path.join(RAW_CALLS_DIR, sha256 + ".csv.gz"), call_rows)
```

Aggregate map load and hit loop:

```57:62:E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py
def load_api_map(path):
    mapping = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            mapping[(row["class"], row["method"])] = row["permissions"]
    return mapping
```

```227:277:E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py
        hits_by = {c: 0 for c in CATS}
        dist_by = {c: set() for c in CATS}
        api_hits_total = 0
        api_hits_sdk = 0
        apis_all = set()
        apis_sdk = set()
        calls_path = os.path.join(cfg.RAW_CALLS_DIR, sha + ".csv.gz")
        if not os.path.exists(calls_path):
            err_rows.append({
                "sha256": sha,
                "section": "raw_calls",
                "exception": "FileNotFoundError",
                "message": "missing %s" % calls_path,
            })
        else:
            try:
                call_rows = load_raw_calls(calls_path)
            except Exception as e:
                err_rows.append({
                    "sha256": sha,
                    "section": "raw_calls",
                    "exception": type(e).__name__,
                    "message": str(e),
                })
                call_rows = None
            if call_rows is not None:
                for cr in call_rows:
                    key = (cr["target_class"], cr["target_method"])
                    perms = api_map.get(key)
                    if perms is None:
                        continue
                    caller = cr["caller_package"] or ""
                    cat, sdk_name, sdk_cat, fw = classify_cached(caller, app_id, catalog, cache)
                    n = cr["n_callsites"]
                    api_hits_total += n
                    hits_by[cat] += n
                    apis_all.add(key)
                    dist_by[cat].add(key)
                    if cat == "sdk":
                        api_hits_sdk += n
                        apis_sdk.add(key)
                    api_rows.append({
                        "sha256": sha,
                        "caller_package": caller,
                        "caller_attribution": cat,
                        "caller_sdk_name": sdk_name,
                        "api_class": cr["target_class"],
                        "api_method": cr["target_method"],
                        "permissions": perms,
                        "n_callsites": n,
                    })
```

Stored A-related fields: `api_hits_total`, `api_hits_sdk`, `api_distinct_overall`, `api_distinct_sdk`, plus per-category `api_hits_*` / `api_distinct_*`. Which of these is “A” is not named in v2. B1.1: because the only map is SEED/TEST, A stays status `unavailable` with reason `Sensitive API map (API 28–33) not finalised`.

### N — network endpoints / hosts

Extract: `const-string` / `const-string/jumbo` → `URL_RE` (`https?|wss?`) → `urlsplit` hostname → `host_keep` (IP or DNS regex). **Denylist is not applied at extract.**

```16:19:E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py
URL_RE = re.compile(r"""(?i)\b(?:https?|wss?)://[^\s"'<>\\]+""")
HOST_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)
```

```97:105:E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py
def host_keep(host):
    if not host:
        return False, False
    host = host.lower().rstrip(".")
    if is_ip_literal(host):
        return True, True
    if HOST_RE.match(host) is None:
        return False, False
    return True, False
```

```272:304:E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py
    try:
        n_unparseable = 0
        host_recs = set()
        for dex in d:
            for cls in dex.get_classes():
                caller_pkg = package_of_class(dotted_class(cls.get_name()))
                for meth in cls.get_methods():
                    code = meth.get_code()
                    if code is None:
                        continue
                    for instr in code.get_bc().get_instructions():
                        if instr.get_name() not in ("const-string", "const-string/jumbo"):
                            continue
                        raw = instr.get_raw_string()
                        if not raw:
                            continue
                        for m in URL_RE.finditer(raw):
                            try:
                                parsed = urlsplit(m.group(0))
                                host = (parsed.hostname or "").lower()
                            except ValueError:
                                n_unparseable += 1
                                continue
                            keep, ip_lit = host_keep(host)
                            if not keep:
                                continue
                            host = host.lower().rstrip(".")
                            host_recs.add((host, caller_pkg, ip_lit))
        out["n_urls_unparseable"] = n_unparseable
        out["hosts"] = [
            {"host": h, "caller_package": pkg, "ip_literal": ip_lit}
            for (h, pkg, ip_lit) in sorted(host_recs, key=lambda x: (x[0], x[1] or "", x[2]))
        ]
```

Aggregate applies `host_denied` then distinct counts:

```201:225:E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py
        hosts_all = set()
        hosts_sdk = set()
        hosts_fp = set()
        for h in obj.get("hosts") or []:
            host = (h.get("host") or "").lower().rstrip(".")
            if host_denied(host):
                continue
            caller = h.get("caller_package") or ""
            cat, sdk_name, sdk_cat, fw = classify_cached(caller, app_id, catalog, cache)
            ip_lit = h.get("ip_literal")
            if ip_lit is None:
                ip_lit = h.get("is_ip_literal")
            host_rows.append({
                "sha256": sha,
                "host": host,
                "caller_package": caller,
                "attribution": cat,
                "sdk_name": sdk_name,
                "ip_literal": ip_lit,
            })
            hosts_all.add(host)
            if cat == "sdk":
                hosts_sdk.add(host)
            if cat == "first_party":
                hosts_fp.add(host)
```

```72:90:E:\AndroZoo\analyzer\pipeline_v2\classify_v2.py
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
```

```108:123:E:\AndroZoo\analyzer\pipeline_v2\config_v2.py
HOST_DENYLIST = [
    "schemas.android.com",
    "www.w3.org",
    "ns.adobe.com",
    "xmlpull.org",
    "www.xmlpull.org",
    "xml.apache.org",
    "schemas.xmlsoap.org",
    "purl.org",
    "json-schema.org",
    "example.com",
    "example.org",
    "example.net",
    "schemas.microsoft.com",
    "schemas.openxmlformats.org",
]
```

Stored N-related fields: `hosts_distinct_all`, `hosts_distinct_sdk`, `hosts_distinct_first_party`. Which of these is “N” is not named in v2. B1.6 says compare `N` — mapping is not chosen here.

### M — manifest fields (v2 has no collapsed flag vector)

v2 stores raw explicit attribute strings and NSC parse facts. It does not build v1-style flags (`debuggable`, `allowBackup`, `cleartext_traffic`, `exported_component`) and does not map them to true/false/indeterminate except `nsc_cleartextTrafficPermitted_true` which is `True`/`False`/`None`.

Extract (namespaced attributes only — D-014):

```308:361:E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py
    try:
        manifest = a.get_android_manifest_xml()
        app = manifest.find("application")
        if app is None:
            out["debuggable_explicit"] = None
            out["allowBackup_explicit"] = None
            out["usesCleartextTraffic_explicit"] = None
            out["networkSecurityConfig"] = None
        else:
            out["debuggable_explicit"] = android_attr(app, "debuggable")
            out["allowBackup_explicit"] = android_attr(app, "allowBackup")
            out["usesCleartextTraffic_explicit"] = android_attr(app, "usesCleartextTraffic")
            out["networkSecurityConfig"] = android_attr(app, "networkSecurityConfig")
        components = []
        for tag in COMPONENT_TAGS:
            for el in manifest.findall(".//" + tag):
                raw_name = android_attr(el, "name")
                resolved = resolve_component_name(raw_name, application_id)
                filters = list(el.findall("intent-filter"))
                is_launcher = False
                for inf in filters:
                    actions = {android_attr(x, "name") for x in inf.findall("action")}
                    cats = {android_attr(x, "name") for x in inf.findall("category")}
                    if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in cats:
                        is_launcher = True
                components.append({
                    "type": tag,
                    "name": resolved,
                    "exported_explicit": android_attr(el, "exported"),
                    "has_intent_filter": len(filters) > 0,
                    "permission": android_attr(el, "permission"),
                    "readPermission": android_attr(el, "readPermission"),
                    "writePermission": android_attr(el, "writePermission"),
                    "is_launcher": is_launcher,
                })
        out["components"] = components
    except Exception as e:
        record_error(errors, "manifest", e)

    try:
        ref = out.get("networkSecurityConfig")
        if ref:
            path, call = resolve_nsc_path(a, ref)
            out["nsc_resolve_call"] = call
            data = a.get_file(path)
            root = AXMLPrinter(data).get_xml_obj()
            out["nsc_parsed"] = True
            out["nsc_error"] = None
            out["nsc_cleartextTrafficPermitted_true"] = parse_nsc_cleartext(root)
    except Exception as e:
        if out.get("networkSecurityConfig"):
            out["nsc_parsed"] = False
            out["nsc_error"] = "%s: %s" % (type(e).__name__, e)
            record_error(errors, "networkSecurityConfig", e)
```

(`COMPONENT_TAGS` line 20: `activity`, `activity-alias`, `service`, `receiver`, `provider`.)

`manifest_v2b.py` is the D-014 re-parser: `android_attr` falls back to a non-namespaced attribute and counts fallbacks (`ns_fallback_manifest_count`). Aggregation **overwrites** extract manifest keys from `raw_manifest/{sha}.json` when that file exists (`aggregate_v2.py:155-161`). Analytic `apk_level.csv` therefore reflects v2b, not extract_v2 alone.

Every M-related field stored on `apk_level.csv`:

| Field | Observed values on 1710 apk_level rows (no SHA printed) |
| --- | --- |
| `debuggable_explicit` | empty 1630, `false` 51, resource refs `@7F040002` (8), `@7F030003` (18), `@7F050002` (3) |
| `allowBackup_explicit` | `true` 777, `false` 390, empty 543 |
| `usesCleartextTraffic_explicit` | `true` 646, `false` 31, empty 1030, three distinct `@7F…` resource refs (1 each) |
| `networkSecurityConfig` | resource / `@xml/` ref or empty |
| `nsc_parsed` | `True` 291, `False` 78, empty 1341 |
| `nsc_error` | empty or the single message below |
| `nsc_cleartextTrafficPermitted_true` | `True` 265, `False` 26, empty 1419 |
| `nsc_resolve_call` | `zip_name_@xml` or `ARSCParser.get_resolved_res_configs` or empty |
| `ns_fallback_manifest_count` | from v2b |
| components (long table) | `exported_explicit`, `has_intent_filter`, `permission`, `readPermission`, `writePermission`, `is_launcher` |

**`ResParserError: res1 must be zero!` handling**

There is no special-case string match. Any exception while resolving/parsing NSC, when `networkSecurityConfig` is set, does:

- `nsc_parsed = False`
- `nsc_error = "{exception_class}: {e}"`
- `nsc_cleartextTrafficPermitted_true` left unchanged (stays `None`; never set to `False` on this path)
- exception appended to `errors` with section `networkSecurityConfig`

On `apk_level.csv` there is exactly one distinct `nsc_error` text, **78** rows:

`ResParserError: res1 must be zero!`

D-015 (`decision_log.md`): “For these APKs the cleartext setting from the network security config is recorded as indeterminate, never as false.” That matches leaving the field `None`. D-015 also says “M is computed with and without these APKs”; **no v2 code computes that with/without M summary**. `errors_long.csv` has 77 `ResParserError` on section `networkSecurityConfig` plus 1 `KeyError` on `AnalyzeAPK` (78 rows). `apk_level` has 78 `nsc_error` ResParserError rows. The 78 vs 77 difference was not attributed (would require printing SHA256).

v1 `MANIFEST_FLAGS` / string-search M in `02_extract_metrics.py:68-88` is **not** v2 and is not quoted as the v2 definition.

### D — SDK footprint (namespace breadth)

Primary formula as implemented (`Lock 5.2` / D-011: `footprint_strict_pct`):

```51:54:E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py
def pct(num, den):
    if den is None or den == 0:
        return None
    return 100.0 * float(num) / float(den)
```

```167:197:E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py
        counts = {c: 0 for c in CATS}
        n_service = 0
        sdk_names = set()
        for pkg, n_classes in packages.items():
            cat, sdk_name, sdk_cat, fw = classify_cached(pkg, app_id, catalog, cache)
            counts[cat] += 1
            assign_n[(pkg, cat, sdk_name, sdk_cat, fw)] += 1
            if cat == "sdk":
                sdk_rows.append({
                    "sha256": sha,
                    "package": pkg,
                    "sdk_name": sdk_name,
                    "sdk_category": sdk_cat,
                    "n_classes": n_classes,
                })
                if sdk_name:
                    sdk_names.add(sdk_name)
                if sdk_cat in cfg.SERVICE_SDK_CATEGORIES:
                    n_service += 1
            elif cat == "unattributed_third_party":
                una_rows.append({
                    "sha256": sha,
                    "package": pkg,
                    "n_classes": n_classes,
                })

        total = sum(counts.values()) if packages else 0
        n_sdk = counts["sdk"]
        n_una = counts["unattributed_third_party"]
        n_tool = counts["toolchain"]
        n_fw = counts["framework"]
```

```311:315:E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py
            "footprint_strict_pct": pct(n_sdk, total),
            "footprint_inclusive_pct": pct(n_sdk + n_una, total),
            "footprint_strict_nontoolchain_pct": pct(n_sdk, total - n_tool - n_fw),
            "footprint_service_pct": pct(n_service, total),
            "n_sdk_distinct": len(sdk_names),
```

As implemented:

- Numerator `n_sdk` = number of **packages** with category `"sdk"`, not class count.
- Denominator `total` = number of packages in the `packages` dict (including empty-string package if present).
- `footprint_strict_pct = 100.0 * n_sdk / total` (`None` if `total == 0`).
- `n_sdk_distinct` = number of distinct `sdk_name` strings among sdk-category packages (names that are empty/None are not added).
- Obfuscated share: no percentage field. Package count is `n_packages_obfuscated` (`counts["obfuscated"]`). Class counts for obfuscated packages are not aggregated into a share field on `apk_level.csv`.
- Service footprint: `footprint_service_pct = 100.0 * n_service / total` where `n_service` counts sdk-category **packages** whose `sdk_category` is in `SERVICE_SDK_CATEGORIES`. `uncertain` and `framework_plugin` are excluded from that numerator (D-012, D-018).

```96:106:E:\AndroZoo\analyzer\pipeline_v2\config_v2.py
SERVICE_SDK_CATEGORIES = {
    "ads",
    "analytics",
    "attribution",
    "crash_reporting",
    "social",
    "payments",
    "maps_location",
    "push_messaging",
    "cloud_backend",
}
```
- B1.6 names `sdk_footprint_pct`, `n_sdk_packages`, `n_total_packages`, `n_sdk_distinct`. Those correspond to v2 columns `footprint_strict_pct`, `n_packages_sdk`, `n_packages_total`, `n_sdk_distinct`. That mapping is B1.6’s naming, not a v2 identifier.

D-013: “the strict footprint is a lower bound in obfuscated apps.” B1.4 requires details note: `namespace breadth, not code volume; lower bound in obfuscated apps`.

### Classifier category ordering

Returned category strings (`classify_package` check order):

1. `toolchain` (`key.startswith` a `TOOLCHAIN_PREFIXES` entry)
2. `framework` (`FRAMEWORK_PREFIXES`; `crc64` matches first segment prefix, not a dot suffix)
3. `first_party` with 5th tuple value `"exact"` (`package == app_id` or `package.startswith(app_id + ".")`) — **before** SDK
4. `sdk` exact `match_type`
5. `sdk` prefix, longest prefix first
6. `first_party` with 5th tuple value `"dev"` (first two segments of `app_id`)
7. `obfuscated` (every segment length `<= 2`)
8. `unattributed_third_party`

The returned category is `"first_party"` for both exact and dev; `"exact"`/`"dev"` are the fifth tuple element, not category names. `aggregate_v2.classify_cached` **drops** the fifth element.

```105:141:E:\AndroZoo\analyzer\pipeline_v2\classify_v2.py
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
```

Aggregation column order (`CATS`), not the classifier check order:

```21:28:E:\AndroZoo\analyzer\pipeline_v2\aggregate_v2.py
CATS = (
    "toolchain",
    "framework",
    "sdk",
    "first_party",
    "obfuscated",
    "unattributed_third_party",
)
```

```16:40:E:\AndroZoo\analyzer\pipeline_v2\config_v2.py
TOOLCHAIN_PREFIXES = [
    "android.",
    "androidx.",
    "android.support.",
    "java.",
    "javax.",
    "kotlin.",
    "kotlinx.",
    "dalvik.",
    "org.jetbrains.",
    "org.intellij.",
    "com.google.android.material.",
    "com.google.errorprone.",
    "com.google.j2objc.",
    "org.checkerframework.",
    "org.codehaus.mojo.",
    "com.google.auto.",
    "org.chromium.support_lib_boundary.",
    "_COROUTINE.",
    "org.junit.",
    "junit.",
    "org.hamcrest.",
    "net.jcip.annotations.",
    "j$.",
]
```

### Framework detection

```42:75:E:\AndroZoo\analyzer\pipeline_v2\config_v2.py
FRAMEWORK_PREFIXES = {
    "flutter": ["io.flutter."],
    "react_native": [
        "com.facebook.react.",
        "com.facebook.hermes.",
        "com.swmansion.",
        "com.facebook.fbreact.",
        "com.facebook.debug.",
        "com.facebook.perftest.",
        "com.facebook.v8.",
        "org.webkit.androidjsc.",
    ],
    "unity": [
        "com.unity3d.player.",
        "bitter.jnibridge.",
        "org.fmod.",
        "com.unity3d.EditorPlugin.",
    ],
    "xamarin_maui": ["mono.android.", "mono.", "crc64", "com.xamarin.", "xamarin."],
    "cordova_capacitor": [
        "org.apache.cordova.",
        "com.getcapacitor.",
        "com.ionicframework.cordova.",
    ],
    "cocos2dx": ["org.cocos2dx."],
}

FRAMEWORK_NATIVE_LIBS = {
    "flutter": ["libflutter.so", "libapp.so"],
    "react_native": ["libreactnativejni.so", "libhermes.so", "libjsc.so"],
    "unity": ["libunity.so", "libil2cpp.so"],
    "xamarin_maui": ["libmonodroid.so", "libmonosgen-2.0.so"],
    "cocos2dx": ["libcocos2dcpp.so", "libcocos2djs.so"],
}
```

```144:167:E:\AndroZoo\analyzer\pipeline_v2\classify_v2.py
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
```

Native-lib basenames come from extract:

```243:249:E:\AndroZoo\analyzer\pipeline_v2\extract_v2.py
        so_bases = set()
        for n in a.zip.namelist():
            parts = n.replace("\\", "/").split("/")
            if len(parts) == 3 and parts[0] == "lib" and parts[2].endswith(".so"):
                so_bases.add(parts[2])
        out["native_libs"] = sorted(so_bases)
```

`aggregate_v2.py:338` stores `frameworks_detected` as `";".join` names. Evidence dict `_fw_ev` is discarded.

---

## B0.5 Inputs v2 needs per APK beyond `metadata.py`

`ROOT\src\analyzer_core\metadata.py` currently returns: `package_name`, `version_name`, `version_code`, `min_sdk`, `target_sdk`, `n_dex_files`, `packages` (sorted distinct Java package **names** via androguard `get_package_class_name`; empty package omitted).

v2 `extract_one` does **not** collect `version_name` / `version_code`.

Additional per-APK inputs v2 uses (these determine the isolation-boundary extension). Androguard `APK` / `DalvikVMFormat` / `Analysis` must stay in the child.

1. **`packages` as `dict[str, int]`** — class count per package, using v2 `dotted_class` + `package_of_class` (strips `$` inner class; default-package `""` is counted). Not the metadata.py name list and not `get_package_class_name`.
2. **`n_classes`**, **`n_methods_defined`** (methods with `get_code() is not None`).
3. **`dex_files`**: `[{name, bytes}, …]` from `a.get_dex_names()` / `a.get_file`; **`total_dex_bytes`**; **`classes_dex_bytes`** (bytes of `classes.dex` only, else `None`).
4. **`permissions_requested`**: `list(a.get_permissions())` — collected; unused by v2 indicators.
5. **`native_libs`**: sorted unique `.so` basenames from zip entries with exactly `lib/<abi>/<name.so>` (three path parts).
6. **`hosts`**: `[{host, caller_package, ip_literal}, …]` from DEX string constants as in B0.4 N.
7. **`n_urls_unparseable`**.
8. **Manifest application attributes** (and, for parity with `apk_level.csv`, the D-014 v2b namespace fallback): `debuggable_explicit`, `allowBackup_explicit`, `usesCleartextTraffic_explicit`, `networkSecurityConfig`.
9. **`components`**: per `activity` / `activity-alias` / `service` / `receiver` / `provider`: `type`, resolved `name`, `exported_explicit`, `has_intent_filter`, `permission`, `readPermission`, `writePermission`, `is_launcher`.
10. **NSC fields**: `nsc_parsed`, `nsc_error`, `nsc_cleartextTrafficPermitted_true`, `nsc_resolve_call`. Requires zip namelist and `a.get_android_resources().get_resolved_res_configs` plus `AXMLPrinter`.
11. **`ns_fallback_manifest_count`** (v2b only; aggregation copies it onto apk-level).
12. **Raw calls**: rows `(caller_package, target_class, target_method, n_callsites)` for non-external methods’ `get_xref_to()` whose target class `startswith("android.")`.
13. **`n_call_rows`**.
14. **`package` / application id** — already overlapping `package_name`, but required for first-party rules and relative component names.

Needed at aggregation (plain data; no androguard object), if indicator computation is in the child as B1.3 requires:

15. Frozen catalog rows (`load_catalog`).
16. `TOOLCHAIN_PREFIXES`, `FRAMEWORK_PREFIXES`, `FRAMEWORK_NATIVE_LIBS`, `HOST_DENYLIST`, `SERVICE_SDK_CATEGORIES`, `SDK_CATEGORY_VOCABULARY`.
17. Sensitive API map — only the SEED file exists; A is unavailable per B1.1.

---

## B0.6 Files created in Phase B0

- `C:\dev\Monarc-sdk\docs\RECON_v2.md` (this file; replaced the previous “E: not mounted” draft)

Temporary helper scripts `_b0_recon.py` and `_b0_recon2.py` were used to hash/count and then deleted. `docs\RECON.md` was not edited. Nothing under `E:\` was written. Phase B1 was not started.

---

## Blockers

1. **P has no v2 implementation.** B1.4/B1.5/B1.6 require filling and asserting/comparing P. HARD CONSTRAINT 6 forbids inventing it from v1 `DANGEROUS_PERMISSIONS` / `02_extract_metrics.py`. B1.1’s “if it is an in-code constant, port the constant verbatim into permissions.py” points at the v1 constant. Those instructions conflict. No P port until that is resolved.
2. **Sensitive API map is SEED/TEST only** (`sensitive_api_map_SEED_TEST.csv`, 12 rows, `source=TEST_SEED_NOT_FOR_RESULTS`). B1.1: do not copy; A stays `unavailable` with reason `Sensitive API map (API 28–33) not finalised`. That part is unambiguous.
3. **M has no derived true/false/indeterminate flag vector in v2**, except NSC cleartext which is `True`/`False`/`None`. B1.4 asks for “M flags with true/false/indeterminate”. Mapping resource refs (`@7F…`), missing attributes, and component `exported_explicit` into those booleans is not implemented. Do not invent it.
4. **Two manifest parsers.** `extract_v2.py` reads namespaced android attributes only. `manifest_v2b.py` (D-014) adds non-namespaced fallback; `aggregate_v2.py` overwrites manifest fields from `raw_manifest`. B1.2 says port extract_v2/classify_v2. Parity with `apk_level.csv` requires the v2b overlay. Which body to port is not chosen here.
5. **B1.6 “v2 sample file” vs ok/error.** `sample_v2.csv` has strata and no extract status. `extract_run_log.csv` has stratum and status but duplicate rows (`skipped_done`). `analytic_sample.csv` `included` is D-019 eligibility (`n_packages_sdk >= 2`), not extract `ok`. Which status filter B1.6 uses is not chosen here.
6. **Which numeric field is A, N, or D’s single `value`.** v2 stores several: A (`api_hits_total` vs `api_hits_sdk` vs distinct counts); N (`hosts_distinct_all` vs `_sdk` vs `_first_party`); D (`footprint_strict_pct` is primary per D-011; B1.6 also requires `n_packages_sdk`, `n_packages_total`, `n_sdk_distinct`). Not chosen here except to record B1.6’s D field list.
7. **`extract_v2.py` / `aggregate_v2.py` / `manifest_v2b.py` are not freeze-listed.** Catalog, `config_v2.py`, `classify_v2.py`, and `validation_key.csv` are frozen and MATCH. Porting extract is required by this prompt but is not a freeze-manifest file.
8. **Package identity differs from current `metadata.py`.** v2 uses `package_of_class` (inner-class `$` strip; empty package kept). `metadata.py` uses `get_package_class_name` and drops empty packages. Reusing the Phase 1A package list would change D’s denominator.
9. **`apk_level.csv` `nsc_error` count (78) ≠ `errors_long.csv` `ResParserError` count (77).** Cause: Cannot determine without printing SHA256.
10. **Phase B1 was not started.**

Ambiguities that this prompt does not cover were not resolved. No indicator, heuristic, catalog row, permission, or API entry was invented.
