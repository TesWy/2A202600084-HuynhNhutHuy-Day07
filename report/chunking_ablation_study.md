# Chunking Ablation Study

- Generated at: `2026-04-10T16:34:58`
- Corpus directory: `D:\VinUni\assignments\Day_7_Lab_data\data`
- Documents evaluated: `8`
- Shared parameters: `chunk_size=1400`, `overlap=150`, `max_sentences=4`
- Notes: non-article strategies trim preamble to the first legal article; structured legal chunking preserves chapter/section breadcrumbs and splits long articles by clauses when needed.

## Strategy Configurations

- `fixed`: strategy=`fixed`, chunk_size=`1400`, overlap=`150`, max_sentences=`4`
- `recursive`: strategy=`recursive`, chunk_size=`1400`, overlap=`150`, max_sentences=`4`
- `sentence`: strategy=`sentence`, chunk_size=`1400`, overlap=`150`, max_sentences=`4`
- `article_simple`: strategy=`article_simple`, chunk_size=`1400`, overlap=`150`, max_sentences=`4`
- `structured_legal`: strategy=`structured_legal`, chunk_size=`1400`, overlap=`150`, max_sentences=`4`

## Corpus Inventory

| # | Document | Language | Domain | Year | Characters | Articles |
|---|---|---|---|---:|---:|---:|
| 1 | Bộ Luật dân sự 2015.txt | vi | Dân sự | 2015 | 371,291 | 689 |
| 2 | Children Law 2016.txt | en | Xã hội | 2016 | 92,195 | 101 |
| 3 | Law on Educators 2025.txt | en | Giáo dục | 2025 | 38,960 | 36 |
| 4 | Law on Investment 2025.txt | en | Kinh tế | 2025 | 106,798 | 47 |
| 5 | Law on Marriage and Family 2014.txt | en | Dân sự | 2014 | 96,219 | 133 |
| 6 | Law on Population 2025.txt | en | Xã hội | 2025 | 29,859 | 27 |
| 7 | Law on Press 2025.txt | en | Xã hội | 2025 | 61,199 | 44 |
| 8 | Planning Law 2025.txt | en | Kinh tế | 2025 | 127,862 | 54 |

## Aggregate Results

| Strategy | Chunks | Avg chunks/doc | Weighted avg len | Avg median len | Oversize ratio | Heading-start ratio | Article coverage | Multi-segment article ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| structured_legal(1400) | 1398 | 174.75 | 757.2 | 899.31 | 0.0 | 1.0 | 1.0 | 0.1238 |
| article_simple | 1131 | 141.38 | 805.58 | 889.19 | 0.107 | 1.0 | 1.0 | 0.0 |
| fixed(1400, overlap=150) | 739 | 92.38 | 1394.75 | 1400.0 | 0.0 | 0.3694 | 1.0 | 0.0 |
| recursive(1400) | 7666 | 958.25 | 118.0 | 81.81 | 0.0 | 0.1475 | 1.0 | 0.0 |
| sentence(max_sentences=4) | 2248 | 281.0 | 406.25 | 354.75 | 0.0111 | 0.1517 | 0.3236 | 0.0 |

## Per-Document Results

### Bộ Luật dân sự 2015.txt

- Recommended strategy: `structured_legal`
| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| article_simple | 689 | 531.93 | 441 | 2689 | 17 | 1.0 | 1.0 | 0 |
| fixed(1400, overlap=150) | 297 | 1398.03 | 1400 | 1400 | 0 | 0.5522 | 1.0 | 0 |
| recursive(1400) | 2957 | 123.45 | 98 | 655 | 0 | 0.233 | 1.0 | 0 |
| sentence(max_sentences=4) | 1017 | 362.02 | 330 | 1486 | 2 | 0.2006 | 0.3164 | 0 |
| structured_legal(1400) | 715 | 623.75 | 558 | 1398 | 0 | 1.0 | 1.0 | 25 |

- Observation: `structured_legal` kept article coverage at `1.0` with `0` oversized chunks, versus `article_simple` having `17` oversized chunks.

### Children Law 2016.txt

- Recommended strategy: `structured_legal`
| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| article_simple | 101 | 899.15 | 836 | 2817 | 22 | 1.0 | 1.0 | 0 |
| fixed(1400, overlap=150) | 74 | 1389.03 | 1400.0 | 1400 | 0 | 0.4054 | 1.0 | 0 |
| recursive(1400) | 682 | 132.35 | 89.0 | 772 | 0 | 0.1481 | 1.0 | 0 |
| sentence(max_sentences=4) | 222 | 409.64 | 396.0 | 1239 | 0 | 0.1171 | 0.2871 | 0 |
| structured_legal(1400) | 133 | 785.05 | 811 | 1399 | 0 | 1.0 | 1.0 | 28 |

- Observation: `structured_legal` kept article coverage at `1.0` with `0` oversized chunks, versus `article_simple` having `22` oversized chunks.

### Law on Educators 2025.txt

- Recommended strategy: `structured_legal`
| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| article_simple | 36 | 1053.83 | 916.0 | 3682 | 10 | 1.0 | 1.0 | 0 |
| fixed(1400, overlap=150) | 31 | 1388.71 | 1400 | 1400 | 0 | 0.129 | 1.0 | 0 |
| recursive(1400) | 381 | 98.84 | 75 | 513 | 0 | 0.0945 | 1.0 | 0 |
| sentence(max_sentences=4) | 102 | 373.47 | 330.0 | 1356 | 0 | 0.1373 | 0.4167 | 0 |
| structured_legal(1400) | 47 | 867.87 | 889 | 1393 | 0 | 1.0 | 1.0 | 10 |

- Observation: `structured_legal` kept article coverage at `1.0` with `0` oversized chunks, versus `article_simple` having `10` oversized chunks.

### Law on Investment 2025.txt

- Recommended strategy: `structured_legal`
| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| article_simple | 47 | 2242.47 | 1421 | 20953 | 24 | 1.0 | 1.0 | 0 |
| fixed(1400, overlap=150) | 85 | 1399.45 | 1400 | 1400 | 0 | 0.1294 | 1.0 | 0 |
| recursive(1400) | 1214 | 85.29 | 33.0 | 712 | 0 | 0.0387 | 1.0 | 0 |
| sentence(max_sentences=4) | 216 | 487.07 | 385.0 | 1916 | 9 | 0.1111 | 0.5106 | 0 |
| structured_legal(1400) | 114 | 1044.65 | 1178.5 | 1400 | 0 | 1.0 | 1.0 | 25 |

- Observation: `structured_legal` kept article coverage at `1.0` with `0` oversized chunks, versus `article_simple` having `24` oversized chunks.

### Law on Marriage and Family 2014.txt

- Recommended strategy: `structured_legal`
| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| article_simple | 133 | 713.38 | 596 | 5969 | 9 | 1.0 | 1.0 | 0 |
| fixed(1400, overlap=150) | 77 | 1392.73 | 1400 | 1400 | 0 | 0.4545 | 1.0 | 0 |
| recursive(1400) | 603 | 156.96 | 125 | 580 | 0 | 0.2206 | 1.0 | 0 |
| sentence(max_sentences=4) | 209 | 456.03 | 417 | 1326 | 0 | 0.1579 | 0.2932 | 0 |
| structured_legal(1400) | 147 | 727.37 | 692 | 1396 | 0 | 1.0 | 1.0 | 11 |

- Observation: `structured_legal` kept article coverage at `1.0` with `0` oversized chunks, versus `article_simple` having `9` oversized chunks.

### Law on Population 2025.txt

- Recommended strategy: `structured_legal`
| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| article_simple | 27 | 1071.37 | 810 | 3505 | 6 | 1.0 | 1.0 | 0 |
| fixed(1400, overlap=150) | 24 | 1371.46 | 1400.0 | 1400 | 0 | 0.2083 | 1.0 | 0 |
| recursive(1400) | 286 | 100.67 | 66.0 | 854 | 0 | 0.0944 | 1.0 | 0 |
| sentence(max_sentences=4) | 85 | 342.36 | 284 | 1239 | 0 | 0.1176 | 0.4074 | 0 |
| structured_legal(1400) | 36 | 867.58 | 873.0 | 1383 | 0 | 1.0 | 1.0 | 6 |

- Observation: `structured_legal` kept article coverage at `1.0` with `0` oversized chunks, versus `article_simple` having `6` oversized chunks.

### Law on Press 2025.txt

- Recommended strategy: `structured_legal`
| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| article_simple | 44 | 1366.07 | 881.0 | 7509 | 11 | 1.0 | 1.0 | 0 |
| fixed(1400, overlap=150) | 49 | 1387.41 | 1400 | 1400 | 0 | 0.1224 | 1.0 | 0 |
| recursive(1400) | 466 | 128.13 | 98.5 | 805 | 0 | 0.0944 | 1.0 | 0 |
| sentence(max_sentences=4) | 149 | 403.8 | 347 | 1895 | 3 | 0.1007 | 0.3409 | 0 |
| structured_legal(1400) | 71 | 927.62 | 1035 | 1397 | 0 | 1.0 | 1.0 | 11 |

- Observation: `structured_legal` kept article coverage at `1.0` with `0` oversized chunks, versus `article_simple` having `11` oversized chunks.

### Planning Law 2025.txt

- Recommended strategy: `structured_legal`
| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| article_simple | 54 | 2343.67 | 1212.5 | 18206 | 22 | 1.0 | 1.0 | 0 |
| fixed(1400, overlap=150) | 102 | 1397.79 | 1400.0 | 1400 | 0 | 0.1765 | 1.0 | 0 |
| recursive(1400) | 1077 | 115.99 | 70 | 933 | 0 | 0.0501 | 1.0 | 0 |
| sentence(max_sentences=4) | 248 | 509.15 | 349.0 | 2545 | 11 | 0.0605 | 0.2778 | 0 |
| structured_legal(1400) | 135 | 1068.76 | 1158 | 1400 | 0 | 1.0 | 1.0 | 24 |

- Observation: `structured_legal` kept article coverage at `1.0` with `0` oversized chunks, versus `article_simple` having `22` oversized chunks.
