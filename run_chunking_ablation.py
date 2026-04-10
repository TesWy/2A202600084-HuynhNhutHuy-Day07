from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path

from src.legal_corpus import (
    chunk_legal_text,
    collect_legal_source_files,
    extract_legal_articles,
    infer_legal_metadata,
)

VI_ARTICLE_WORD = "\u0110i\u1ec1u"
ARTICLE_REFERENCE_PATTERN = re.compile(rf"(?:{VI_ARTICLE_WORD}|Article)\s+(\d+)", flags=re.IGNORECASE)
ARTICLE_HEADING_PATTERN = re.compile(rf"(?m)^(?:{VI_ARTICLE_WORD}|Article)\s+(\d+)\b", flags=re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a chunking ablation study on the legal corpus.")
    parser.add_argument("--data-dir", default="data", help="Directory containing legal source files.")
    parser.add_argument("--sample-files", type=int, default=0, help="Only evaluate the first N legal files.")
    parser.add_argument("--chunk-size", type=int, default=1400, help="Chunk size budget used by chunk-based strategies.")
    parser.add_argument("--overlap", type=int, default=150, help="Overlap for fixed-size chunking.")
    parser.add_argument("--max-sentences", type=int, default=4, help="Sentence budget for sentence chunking.")
    parser.add_argument(
        "--output-md",
        default="report/chunking_ablation_study.md",
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--output-json",
        default="report/chunking_ablation_study.json",
        help="JSON report output path.",
    )
    return parser.parse_args()


def strategy_configs(args: argparse.Namespace) -> list[dict[str, object]]:
    return [
        {
            "name": "fixed",
            "label": f"fixed({args.chunk_size}, overlap={args.overlap})",
            "strategy": "fixed",
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "max_sentences": args.max_sentences,
        },
        {
            "name": "recursive",
            "label": f"recursive({args.chunk_size})",
            "strategy": "recursive",
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "max_sentences": args.max_sentences,
        },
        {
            "name": "sentence",
            "label": f"sentence(max_sentences={args.max_sentences})",
            "strategy": "sentence",
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "max_sentences": args.max_sentences,
        },
        {
            "name": "article_simple",
            "label": "article_simple",
            "strategy": "article_simple",
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "max_sentences": args.max_sentences,
        },
        {
            "name": "structured_legal",
            "label": f"structured_legal({args.chunk_size})",
            "strategy": "structured_legal",
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "max_sentences": args.max_sentences,
        },
    ]


def article_heading_near_start(text: str) -> bool:
    non_empty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in non_empty_lines[:3]:
        if ARTICLE_REFERENCE_PATTERN.match(line):
            return True
    return False


def compute_chunk_metrics(path: Path, config: dict[str, object]) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    metadata = infer_legal_metadata(path, text=text)
    article_records = extract_legal_articles(text)
    total_articles = len(article_records)
    source_article_ids = {str(article.get("article_number") or "").strip() for article in article_records if article.get("article_number")}

    chunks = chunk_legal_text(
        text,
        strategy=str(config["strategy"]),
        chunk_size=int(config["chunk_size"]),
        overlap=int(config["overlap"]),
        max_sentences=int(config["max_sentences"]),
    )

    chunk_lengths = [len(chunk.content) for chunk in chunks]
    distinct_article_hits: set[str] = set()
    heading_start_count = 0
    multi_segment_articles: set[str] = set()

    for chunk in chunks:
        if article_heading_near_start(chunk.content):
            heading_start_count += 1
        distinct_article_hits.update(ARTICLE_HEADING_PATTERN.findall(chunk.content))
        article_number = str(chunk.metadata.get("article_number") or "").strip()
        if article_number and int(chunk.metadata.get("segment_count", 1)) > 1:
            multi_segment_articles.add(article_number)

    oversized_chunks = sum(1 for length in chunk_lengths if length > int(config["chunk_size"]))
    covered_article_ids = distinct_article_hits.intersection(source_article_ids)
    article_coverage_ratio = (len(covered_article_ids) / total_articles) if total_articles else 0.0
    heading_start_ratio = (heading_start_count / len(chunks)) if chunks else 0.0
    oversize_ratio = (oversized_chunks / len(chunks)) if chunks else 0.0

    return {
        "document": path.name,
        "document_title": metadata["document_title"],
        "domain": metadata["domain"],
        "year": metadata["year"],
        "language": metadata["language"],
        "char_count": len(text),
        "total_articles": total_articles,
        "strategy": str(config["name"]),
        "strategy_label": str(config["label"]),
        "chunk_count": len(chunks),
        "avg_length": round((sum(chunk_lengths) / len(chunks)) if chunks else 0.0, 2),
        "median_length": round(statistics.median(chunk_lengths), 2) if chunk_lengths else 0.0,
        "min_length": min(chunk_lengths) if chunk_lengths else 0,
        "max_length": max(chunk_lengths) if chunk_lengths else 0,
        "oversized_chunks": oversized_chunks,
        "oversize_ratio": round(oversize_ratio, 4),
        "heading_start_count": heading_start_count,
        "heading_start_ratio": round(heading_start_ratio, 4),
        "article_hits": len(covered_article_ids),
        "article_coverage_ratio": round(article_coverage_ratio, 4),
        "multi_segment_articles": len(multi_segment_articles),
        "multi_segment_ratio": round((len(multi_segment_articles) / total_articles) if total_articles else 0.0, 4),
    }


def pick_recommended_strategy(records: list[dict[str, object]]) -> str:
    best = max(
        records,
        key=lambda record: (
            float(record["article_coverage_ratio"]),
            float(record["heading_start_ratio"]),
            -float(record["oversize_ratio"]),
            -int(record["chunk_count"]),
        ),
    )
    return str(best["strategy"])


def aggregate_by_strategy(records: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for record in records:
        grouped.setdefault(str(record["strategy"]), []).append(record)

    summary: list[dict[str, object]] = []
    for strategy_name, strategy_records in grouped.items():
        total_chunks = sum(int(record["chunk_count"]) for record in strategy_records)
        total_articles = sum(int(record["total_articles"]) for record in strategy_records)
        total_article_hits = sum(int(record["article_hits"]) for record in strategy_records)
        total_heading_starts = sum(int(record["heading_start_count"]) for record in strategy_records)
        total_oversized = sum(int(record["oversized_chunks"]) for record in strategy_records)
        total_multisegment = sum(int(record["multi_segment_articles"]) for record in strategy_records)
        weighted_chars = sum(int(record["avg_length"] * record["chunk_count"]) for record in strategy_records)

        summary.append(
            {
                "strategy": strategy_name,
                "strategy_label": strategy_records[0]["strategy_label"],
                "documents": len(strategy_records),
                "total_chunks": total_chunks,
                "avg_chunks_per_doc": round(total_chunks / len(strategy_records), 2),
                "weighted_avg_length": round((weighted_chars / total_chunks) if total_chunks else 0.0, 2),
                "avg_median_length": round(
                    sum(float(record["median_length"]) for record in strategy_records) / len(strategy_records), 2
                ),
                "oversize_ratio": round((total_oversized / total_chunks) if total_chunks else 0.0, 4),
                "heading_start_ratio": round((total_heading_starts / total_chunks) if total_chunks else 0.0, 4),
                "article_coverage_ratio": round((total_article_hits / total_articles) if total_articles else 0.0, 4),
                "multi_segment_ratio": round((total_multisegment / total_articles) if total_articles else 0.0, 4),
            }
        )

    return sorted(
        summary,
        key=lambda record: (
            -float(record["article_coverage_ratio"]),
            -float(record["heading_start_ratio"]),
            float(record["oversize_ratio"]),
            float(record["avg_chunks_per_doc"]),
        ),
    )


def render_markdown(
    source_files: list[Path],
    configs: list[dict[str, object]],
    records: list[dict[str, object]],
    aggregates: list[dict[str, object]],
    args: argparse.Namespace,
) -> str:
    generated_at = datetime.now().isoformat(timespec="seconds")
    by_document: dict[str, list[dict[str, object]]] = {}
    for record in records:
        by_document.setdefault(str(record["document"]), []).append(record)

    lines = [
        "# Chunking Ablation Study",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Corpus directory: `{Path(args.data_dir).resolve()}`",
        f"- Documents evaluated: `{len(source_files)}`",
        f"- Shared parameters: `chunk_size={args.chunk_size}`, `overlap={args.overlap}`, `max_sentences={args.max_sentences}`",
        "- Notes: non-article strategies trim preamble to the first legal article; structured legal chunking preserves chapter/section breadcrumbs and splits long articles by clauses when needed.",
        "",
        "## Strategy Configurations",
        "",
    ]
    for config in configs:
        lines.append(
            f"- `{config['name']}`: strategy=`{config['strategy']}`, chunk_size=`{config['chunk_size']}`, "
            f"overlap=`{config['overlap']}`, max_sentences=`{config['max_sentences']}`"
        )

    lines.extend(
        [
            "",
            "## Corpus Inventory",
            "",
            "| # | Document | Language | Domain | Year | Characters | Articles |",
            "|---|---|---|---|---:|---:|---:|",
        ]
    )
    inventory_records = {str(record["document"]): record for record in records if str(record["strategy"]) == "structured_legal"}
    for index, path in enumerate(source_files, start=1):
        record = inventory_records[path.name]
        lines.append(
            f"| {index} | {path.name} | {record['language']} | {record['domain']} | "
            f"{record['year'] or ''} | {record['char_count']:,} | {record['total_articles']} |"
        )

    lines.extend(
        [
            "",
            "## Aggregate Results",
            "",
            "| Strategy | Chunks | Avg chunks/doc | Weighted avg len | Avg median len | Oversize ratio | Heading-start ratio | Article coverage | Multi-segment article ratio |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for aggregate in aggregates:
        lines.append(
            f"| {aggregate['strategy_label']} | {aggregate['total_chunks']} | {aggregate['avg_chunks_per_doc']} | "
            f"{aggregate['weighted_avg_length']} | {aggregate['avg_median_length']} | {aggregate['oversize_ratio']} | "
            f"{aggregate['heading_start_ratio']} | {aggregate['article_coverage_ratio']} | {aggregate['multi_segment_ratio']} |"
        )

    lines.extend(["", "## Per-Document Results", ""])
    for path in source_files:
        doc_records = sorted(by_document[path.name], key=lambda record: str(record["strategy"]))
        recommended = pick_recommended_strategy(doc_records)
        lines.append(f"### {path.name}")
        lines.append("")
        lines.append(f"- Recommended strategy: `{recommended}`")
        lines.append(
            "| Strategy | Chunks | Avg len | Median len | Max len | Oversized | Heading-start | Article coverage | Multi-segment articles |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for record in doc_records:
            lines.append(
                f"| {record['strategy_label']} | {record['chunk_count']} | {record['avg_length']} | "
                f"{record['median_length']} | {record['max_length']} | {record['oversized_chunks']} | "
                f"{record['heading_start_ratio']} | {record['article_coverage_ratio']} | {record['multi_segment_articles']} |"
            )

        structured = next(record for record in doc_records if str(record["strategy"]) == "structured_legal")
        article_simple = next(record for record in doc_records if str(record["strategy"]) == "article_simple")
        lines.append("")
        lines.append(
            f"- Observation: `structured_legal` kept article coverage at `{structured['article_coverage_ratio']}` "
            f"with `{structured['oversized_chunks']}` oversized chunks, versus `article_simple` having "
            f"`{article_simple['oversized_chunks']}` oversized chunks."
        )
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    data_dir = Path(args.data_dir).resolve()
    source_files = collect_legal_source_files(data_dir)
    if args.sample_files > 0:
        source_files = source_files[: args.sample_files]

    if not source_files:
        print(f"No legal source files found in {data_dir}")
        return 1

    configs = strategy_configs(args)
    records: list[dict[str, object]] = []

    for path in source_files:
        print(f"Evaluating {path.name} ...")
        for config in configs:
            record = compute_chunk_metrics(path, config)
            records.append(record)
            print(
                f"  {config['name']}: chunks={record['chunk_count']}, "
                f"coverage={record['article_coverage_ratio']}, oversize={record['oversized_chunks']}"
            )

    aggregates = aggregate_by_strategy(records)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_dir": str(data_dir),
        "parameters": {
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "max_sentences": args.max_sentences,
        },
        "strategies": configs,
        "records": records,
        "aggregates": aggregates,
    }

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(source_files, configs, records, aggregates, args), encoding="utf-8")

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"Markdown report: {output_md.resolve()}")
    print(f"JSON report: {output_json.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
