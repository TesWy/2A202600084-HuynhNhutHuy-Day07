from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter

from src import build_legal_chunk_documents, collect_legal_source_files, load_embedder_from_env
from src.persistent_vector_store import PersistentVectorStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index the full legal corpus and evaluate golden queries.")
    parser.add_argument("--data-dir", default="data", help="Directory containing legal source files.")
    parser.add_argument("--collection", default="legal_full_structured", help="Persistent collection name.")
    parser.add_argument("--persist-dir", default=".vector_store", help="Directory for persistent vector store files.")
    parser.add_argument(
        "--cache-path",
        default=".vector_store/embedding_cache.json",
        help="Persistent embedding cache file.",
    )
    parser.add_argument(
        "--golden-file",
        default="report/golden_queries_legal.json",
        help="JSON file containing golden queries and expected answers.",
    )
    parser.add_argument(
        "--strategy",
        choices=["structured_legal", "article_simple", "fixed", "recursive", "sentence"],
        default="structured_legal",
        help="Chunking strategy used for indexing.",
    )
    parser.add_argument("--chunk-size", type=int, default=1400, help="Chunk size budget.")
    parser.add_argument("--overlap", type=int, default=150, help="Overlap for fixed chunking.")
    parser.add_argument("--max-sentences", type=int, default=4, help="Sentence budget for sentence chunking.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of retrieval results to evaluate.")
    parser.add_argument("--reindex", action="store_true", help="Rebuild the persistent collection before evaluation.")
    parser.add_argument(
        "--allow-mock",
        action="store_true",
        help="Allow fallback to the mock embedder. By default the script exits if no real embedding backend is active.",
    )
    parser.add_argument(
        "--output-md",
        default="report/golden_query_results.md",
        help="Markdown output path.",
    )
    parser.add_argument(
        "--output-json",
        default="report/golden_query_results.json",
        help="JSON output path.",
    )
    return parser.parse_args()


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def keyword_recall(text: str, keywords: list[str]) -> tuple[float, list[str]]:
    if not keywords:
        return 1.0, []
    normalized = normalize_text(text)
    matched = [keyword for keyword in keywords if normalize_text(keyword) in normalized]
    return len(matched) / len(keywords), matched


def load_golden_queries(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_index(
    store: PersistentVectorStore,
    args: argparse.Namespace,
    data_dir: Path,
) -> tuple[int, int]:
    source_files = collect_legal_source_files(data_dir)
    if args.reindex or store.count() == 0:
        store.clear()
        overall_start = perf_counter()
        for file_index, source_file in enumerate(source_files, start=1):
            file_start = perf_counter()
            docs = build_legal_chunk_documents(
                source_file,
                strategy=args.strategy,
                chunk_size=args.chunk_size,
                overlap=args.overlap,
                max_sentences=args.max_sentences,
            )
            print(f"[{file_index}/{len(source_files)}] Indexing {source_file.name}: chunks={len(docs)}")
            progress_every = max(25, len(docs) // 10 or 1)

            def _progress(stats: dict[str, int]) -> None:
                print(
                    f"  processed {stats['processed']}/{stats['total']} chunks "
                    f"(cache hits={stats['cache_hits']}, misses={stats['cache_misses']})"
                )

            stats = store.add_documents(
                docs,
                replace_doc_ids=True,
                progress_callback=_progress,
                progress_every=progress_every,
            )
            print(
                f"  done in {perf_counter() - file_start:.1f}s "
                f"(cache hits={stats['cache_hits']}, misses={stats['cache_misses']})"
            )
        print(f"Indexing finished in {perf_counter() - overall_start:.1f}s")
    return len(source_files), store.count()


def evaluate_mode(
    store: PersistentVectorStore,
    queries: list[dict[str, object]],
    top_k: int,
    mode: str,
) -> dict[str, object]:
    results: list[dict[str, object]] = []

    for item in queries:
        metadata_filter = item.get("metadata_filter", {}) if mode == "gold_filter" else {}
        if metadata_filter:
            retrieved = store.search_with_filter(
                str(item["query"]),
                metadata_filter=dict(metadata_filter),
                top_k=top_k,
            )
        else:
            retrieved = store.search(str(item["query"]), top_k=top_k)

        expected_title = str(item.get("expected_document_title") or "")
        expected_article = str(item.get("expected_article_number") or "")

        top1 = retrieved[0] if retrieved else None
        top_titles = [str(result["metadata"].get("document_title") or "") for result in retrieved]
        top_articles = [str(result["metadata"].get("article_number") or "") for result in retrieved]
        top1_exact = bool(
            top1
            and str(top1["metadata"].get("document_title") or "") == expected_title
            and str(top1["metadata"].get("article_number") or "") == expected_article
        )
        top3_exact = any(title == expected_title and article == expected_article for title, article in zip(top_titles, top_articles))

        combined_text = "\n\n".join(result["content"] for result in retrieved)
        recall, matched_keywords = keyword_recall(combined_text, list(item.get("must_include_keywords", [])))
        min_recall = float(item.get("min_keyword_recall", 0.5))
        passed = top3_exact and recall >= min_recall

        results.append(
            {
                "id": item["id"],
                "query": item["query"],
                "gold_answer": item["gold_answer"],
                "mode": mode,
                "metadata_filter": metadata_filter,
                "expected_document_title": expected_title,
                "expected_article_number": expected_article,
                "top1_exact_match": top1_exact,
                "top3_exact_match": top3_exact,
                "keyword_recall_topk": round(recall, 4),
                "matched_keywords": matched_keywords,
                "passed": passed,
                "results": [
                    {
                        "rank": index,
                        "score": result["score"],
                        "document_title": result["metadata"].get("document_title"),
                        "article_number": result["metadata"].get("article_number"),
                        "language": result["metadata"].get("language"),
                        "preview": result["content"][:220].replace("\n", " "),
                    }
                    for index, result in enumerate(retrieved, start=1)
                ],
            }
        )

    summary = {
        "mode": mode,
        "queries": len(results),
        "top1_exact_rate": round(sum(1 for item in results if item["top1_exact_match"]) / len(results), 4),
        "top3_exact_rate": round(sum(1 for item in results if item["top3_exact_match"]) / len(results), 4),
        "pass_rate": round(sum(1 for item in results if item["passed"]) / len(results), 4),
        "avg_keyword_recall": round(sum(float(item["keyword_recall_topk"]) for item in results) / len(results), 4),
    }
    return {"summary": summary, "queries": results}


def render_markdown(
    payload: dict[str, object],
) -> str:
    lines = [
        "# Golden Query Evaluation",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Embedding backend: `{payload['embedding_backend']}`",
        f"- Collection: `{payload['collection']}`",
        f"- Strategy: `{payload['strategy']}`",
        f"- Parameters: `chunk_size={payload['parameters']['chunk_size']}`, `overlap={payload['parameters']['overlap']}`, `max_sentences={payload['parameters']['max_sentences']}`, `top_k={payload['parameters']['top_k']}`",
        f"- Source files indexed: `{payload['source_files']}`",
        f"- Stored chunks: `{payload['stored_chunks']}`",
        "",
    ]

    if "mock" in str(payload["embedding_backend"]).lower():
        lines.append("- Warning: current run uses mock embeddings fallback, so semantic ranking quality is not representative of a real embedding backend.")
        lines.append("")

    for evaluation in payload["evaluations"]:
        summary = evaluation["summary"]
        lines.append(f"## Mode: `{summary['mode']}`")
        lines.append("")
        lines.append(
            f"- top1 exact rate: `{summary['top1_exact_rate']}` | "
            f"top3 exact rate: `{summary['top3_exact_rate']}` | "
            f"pass rate: `{summary['pass_rate']}` | "
            f"avg keyword recall: `{summary['avg_keyword_recall']}`"
        )
        lines.append("")
        lines.append("| ID | Query | Expected | Top-1 | Top-3 exact | Keyword recall | Pass |")
        lines.append("|---|---|---|---|---|---:|---|")
        for item in evaluation["queries"]:
            top1 = item["results"][0] if item["results"] else {}
            top1_label = (
                f"{top1.get('document_title', 'None')} / {top1.get('article_number', '')}"
                if top1
                else "None"
            )
            lines.append(
                f"| {item['id']} | {item['query']} | {item['expected_document_title']} / {item['expected_article_number']} | "
                f"{top1_label} | {item['top3_exact_match']} | {item['keyword_recall_topk']} | {item['passed']} |"
            )
        lines.append("")

        for item in evaluation["queries"]:
            lines.append(f"### {item['id']}: {item['query']}")
            lines.append("")
            if item["metadata_filter"]:
                lines.append(f"- Metadata filter: `{item['metadata_filter']}`")
            lines.append(f"- Gold answer: {item['gold_answer']}")
            lines.append(
                f"- Metrics: top1_exact=`{item['top1_exact_match']}`, top3_exact=`{item['top3_exact_match']}`, "
                f"keyword_recall=`{item['keyword_recall_topk']}`, pass=`{item['passed']}`"
            )
            for result in item["results"]:
                lines.append(
                    f"- Top-{result['rank']}: score=`{result['score']:.4f}`, "
                    f"title=`{result['document_title']}`, article=`{result['article_number']}`, preview=`{result['preview']}`"
                )
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    data_dir = Path(args.data_dir).resolve()
    golden_file = Path(args.golden_file).resolve()

    embedder = load_embedder_from_env(default_provider="local")
    backend_name = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    if "mock" in backend_name.lower() and not args.allow_mock:
        print("No real embedding backend detected. Set EMBEDDING_PROVIDER and API/model env vars, or pass --allow-mock.")
        return 1

    store = PersistentVectorStore(
        collection_name=args.collection,
        embedding_fn=embedder,
        persist_dir=args.persist_dir,
        cache_path=args.cache_path,
    )
    source_files, stored_chunks = ensure_index(store, args, data_dir)
    golden_queries = load_golden_queries(golden_file)

    evaluations = [
        evaluate_mode(store, golden_queries, args.top_k, mode="no_filter"),
        evaluate_mode(store, golden_queries, args.top_k, mode="gold_filter"),
    ]

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "embedding_backend": backend_name,
        "collection": args.collection,
        "strategy": args.strategy,
        "parameters": {
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "max_sentences": args.max_sentences,
            "top_k": args.top_k,
        },
        "source_files": source_files,
        "stored_chunks": stored_chunks,
        "golden_file": str(golden_file),
        "evaluations": evaluations,
    }

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload), encoding="utf-8")

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Embedding backend: {payload['embedding_backend']}")
    print(f"Indexed source files: {source_files}")
    print(f"Stored chunks: {stored_chunks}")
    for evaluation in evaluations:
        summary = evaluation["summary"]
        print(
            f"Mode={summary['mode']}: top1_exact_rate={summary['top1_exact_rate']}, "
            f"top3_exact_rate={summary['top3_exact_rate']}, pass_rate={summary['pass_rate']}, "
            f"avg_keyword_recall={summary['avg_keyword_recall']}"
        )
    print(f"Markdown report: {output_md.resolve()}")
    print(f"JSON report: {output_json.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
