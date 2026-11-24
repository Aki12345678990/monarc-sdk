# Parity against the frozen v2 pipeline

Date: 2026-11-24

Engine: analyzer_core 0.2.0

Source of truth: `E:\AndroZoo\analyzer\results_v2\stats\analysis_dataset.csv`, the table `stats_v2.load_dataset_rows` reads when it writes `hypotheses.csv`. Included rows only. On these 30 APKs that file agrees with `indicators_v2.csv` on every compared column.

Sample: `scripts/parity_check.py`, seed 42, 2 APKs per stratum, validation set excluded. 30 APKs. Local read-only copies under `E:\AndroZoo\apks`.

Frozen file SHA-256:

| File | SHA-256 |
| --- | --- |
| `analysis_dataset.csv` | `2a8f6a5d62d3172a09303b8e87810f357d1a292026d967fc9bf3ed0f4b88999b` |
| `indicators_v2.csv` | `e4dc1b6f2af7cb5eae66ed22ffa46fc7b093af057bcf1bb1dc6a4e2a5ffa0cec` |
| `indicators_v2.py` | `321eaad3b0d07eb27605a666fb2648e1dcc17d465857387124c9f88945f24ac2` |
| `hypotheses.csv` | `be8b6220a6a34d9eabaf9dc5a3cc8dcc61b4b29dbfcbbefaa0e3a015923d16d8` |

Floats match within 1e-9. Integers match exactly.

| Column | n compared | n matching | max absolute difference |
| --- | ---: | ---: | ---: |
| P | 30 | 30 | 0 |
| A | 30 | 30 | 0 |
| N | 30 | 30 | 0 |
| N_all | 30 | 30 | 0 |
| D | 30 | 30 | 0 |
| M_exp | 30 | 30 | 0 |
| M_exp_sdk | 30 | 30 | 0 |
| F_debug | 30 | 30 | 0 |
| F_backup | 30 | 30 | 0 |
| F_cleartext | 30 | 30 | 0 |
| M_flags | 30 | 30 | 0 |
| R | 30 | 30 | 0 |
| R_minusD | 30 | 30 | 1.11e-16 |

30/30 APKs, all indicators identical to the research pipeline.

Timing on the three largest local APKs at or under 150 MiB. Each run is a fresh process. Peak is `PeakWorkingSetSize`.

| APK prefix | bytes | seconds | peak MiB |
| --- | ---: | ---: | ---: |
| `5AAD54A378ABBBAD` | 157,177,602 | 11.9 | 893.4 |
| `892430129511BE0C` | 156,682,793 | 65.0 | 2060.6 |
| `D82309C6F9F70522` | 153,310,503 | 166.4 | 3202.0 |

Every run is under 600 seconds.
