from __future__ import annotations

import argparse
import re
import sys
from time import perf_counter
from pathlib import Path

from src import build_legal_chunk_documents, collect_legal_source_files, load_embedder_from_env
from src.persistent_vector_store import PersistentVectorStore


DEFAULT_SAMPLE_QUERIES = [
    "\u0110i\u1ec1u 1 quy \u0111\u1ecbnh ph\u1ea1m vi \u0111i\u1ec1u ch\u1ec9nh c\u1ee7a B\u1ed9 lu\u1eadt d\u00e2n s\u1ef1 2015 l\u00e0 g\u00ec?",
    "\u0110i\u1ec1u 3 n\u00eau c\u00e1c nguy\u00ean t\u1eafc c\u01a1 b\u1ea3n c\u1ee7a ph\u00e1p lu\u1eadt d\u00e2n s\u1ef1 nh\u01b0 th\u1ebf n\u00e0o?",
    "Article 1 of the Planning Law 2025 covers what scope?",
    "Lu\u1eadt n\u00e0o li\u00ean quan \u0111\u1ebfn \u0111\u1ea7u t\u01b0?",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index legal documents into a persistent vector store.")
    parser.add_argument("--data-dir", default="data", help="Directory containing legal .txt/.md files.")
    parser.add_argument("--collection", default="legal_corpus", help="Persistent collection name.")
    parser.add_argument(
        "--strategy",
        choices=["structured_legal", "article_simple", "fixed", "recursive", "sentence"],
        default="structured_legal",
        help="Chunking strategy used before indexing.",
    )
    parser.add_argument("--persist-dir", default=".vector_store", help="Directory for persistent store files.")
    parser.add_argument(
        "--cache-path",
        default=".vector_store/embedding_cache.json",
        help="Path for the persistent embedding cache file.",
    )
    parser.add_argument(
        "--sample-files",
        type=int,
        default=0,
        help="Index only the first N legal source files for a quick test.",
    )
    parser.add_argument(
        "--max-chunks-per-doc",
        type=int,
        default=0,
        help="Optionally limit chunks per document during a quick test.",
    )
    parser.add_argument("--chunk-size", type=int, default=1400, help="Chunk size budget for chunkers that use it.")
    parser.add_argument("--overlap", type=int, default=150, help="Overlap for fixed-size chunking.")
    parser.add_argument("--max-sentences", type=int, default=4, help="Sentence budget for sentence chunking.")
    parser.add_argument("--reset", action="store_true", help="Clear the collection before indexing.")
    parser.add_argument(
        "--query",
        action="append",
        dest="queries",
        help="Optional smoke-test query to run after indexing. Repeat to add multiple queries.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of retrieval results to show for each smoke-test query.",
    )
    parser.add_argument(
        "--no-smoke-test",
        action="store_true",
        help="Skip running the smoke-test queries after indexing.",
    )
    return parser.parse_args()


def extract_article_number(query: str) -> str | None:
    match = re.search(r"(?:\u0110i\u1ec1u|Article)\s+(\d+)", query, flags=re.IGNORECASE)
    return match.group(1) if match else None


def print_results(store: PersistentVectorStore, query: str, top_k: int) -> None:
    article_number = extract_article_number(query)
    if article_number:
        results = store.search_with_filter(query, metadata_filter={"article_number": article_number}, top_k=top_k)
        print(f"Query: {query}")
        print(f"  Applied metadata filter: {{'article_number': '{article_number}'}}")
    else:
        results = store.search(query, top_k=top_k)
        print(f"Query: {query}")
    if not results:
        print("  No results.")
        return

    for rank, result in enumerate(results, start=1):
        preview = result["content"][:180].replace("\n", " ")
        print(
            f"  Top-{rank}: score={result['score']:.4f}, "
            f"title={result['metadata'].get('document_title')}, "
            f"article={result['metadata'].get('article_number')}, "
            f"language={result['metadata'].get('language')}, preview={preview}"
        )


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return 1

    source_files = collect_legal_source_files(data_dir)
    if args.sample_files > 0:
        source_files = source_files[: args.sample_files]

    if not source_files:
        print(f"No legal source files found in {data_dir}")
        return 1

    embedder = load_embedder_from_env(default_provider="gemini")
    store = PersistentVectorStore(
        collection_name=args.collection,
        embedding_fn=embedder,
        persist_dir=args.persist_dir,
        cache_path=args.cache_path,
    )

    print(f"Embedding backend: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}")
    print(f"Collection: {args.collection}")
    print(f"Source files: {len(source_files)}")
    print(
        f"Chunking: strategy={args.strategy}, chunk_size={args.chunk_size}, "
        f"overlap={args.overlap}, max_sentences={args.max_sentences}"
    )

    if args.reset:
        store.clear()
        print("Collection cleared before indexing.")

    overall_start = perf_counter()
    for file_index, source_file in enumerate(source_files, start=1):
        file_start = perf_counter()
        chunk_docs = build_legal_chunk_documents(
            source_file,
            max_chunks=args.max_chunks_per_doc,
            strategy=args.strategy,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            max_sentences=args.max_sentences,
        )
        if not chunk_docs:
            print(f"Skipped empty document: {source_file.name}")
            continue

        metadata = chunk_docs[0].metadata
        print(
            f"[{file_index}/{len(source_files)}] Indexing {source_file.name}: chunks={len(chunk_docs)}, "
            f"domain={metadata.get('domain')}, year={metadata.get('year')}, "
            f"type={metadata.get('document_type')}, language={metadata.get('language')}"
        )
        progress_every = max(25, len(chunk_docs) // 10 or 1)

        def _progress(stats: dict[str, int]) -> None:
            print(
                f"  processed {stats['processed']}/{stats['total']} chunks "
                f"(cache hits={stats['cache_hits']}, misses={stats['cache_misses']})"
            )

        add_stats = store.add_documents(
            chunk_docs,
            replace_doc_ids=True,
            progress_callback=_progress,
            progress_every=progress_every,
        )
        elapsed = perf_counter() - file_start
        print(
            f"  done in {elapsed:.1f}s "
            f"(cache hits={add_stats['cache_hits']}, misses={add_stats['cache_misses']})"
        )

    total_elapsed = perf_counter() - overall_start
    print(f"Persistent store size: {store.count()} chunks")
    print(f"Total indexing time: {total_elapsed:.1f}s")

    if not args.no_smoke_test:
        queries = args.queries or DEFAULT_SAMPLE_QUERIES
        print()
        print("=== Smoke Test Queries ===")
        for query in queries:
            print_results(store, query, args.top_k)
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
