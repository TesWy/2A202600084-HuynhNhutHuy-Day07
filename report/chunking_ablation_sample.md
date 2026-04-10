# Chunking Ablation Study

- Generated at: `2026-04-10T16:33:40`
- Corpus directory: `D:\VinUni\assignments\Day_7_Lab_data\data`
- Documents evaluated: `2`
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

## Aggregate Results

| Strategy | Chunks | Avg chunks/doc | Weighted avg len | Avg median len | Oversize ratio | Heading-start ratio | Article coverage | Multi-segment article ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| structured_legal(1400) | 848 | 424.0 | 649.05 | 684.5 | 0.0 | 1.0 | 1.0 | 0.0671 |
| article_simple | 790 | 395.0 | 578.88 | 638.5 | 0.0494 | 1.0 | 1.0 | 0.0 |
| fixed(1400, overlap=150) | 371 | 185.5 | 1396.23 | 1400.0 | 0.0 | 0.5229 | 1.0 | 0.0 |
| recursive(1400) | 3639 | 1819.5 | 125.12 | 93.5 | 0.0 | 0.2171 | 1.0 | 0.0 |
| sentence(max_sentences=4) | 1239 | 619.5 | 370.55 | 363.0 | 0.0016 | 0.1856 | 0.3127 | 0.0 |

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
