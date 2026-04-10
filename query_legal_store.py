from __future__ import annotations

import argparse
import re
import sys

from src import load_embedder_from_env
from src.persistent_vector_store import PersistentVectorStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query an indexed legal vector store.")
    parser.add_argument("--collection", default="legal_corpus", help="Collection name to query.")
    parser.add_argument("--persist-dir", default=".vector_store", help="Directory containing persistent store files.")
    parser.add_argument(
        "--cache-path",
        default=".vector_store/embedding_cache.json",
        help="Path for the persistent embedding cache file.",
    )
    parser.add_argument("--query", required=True, help="Query text.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of results to show.")
    parser.add_argument("--domain", help="Optional domain filter.")
    parser.add_argument("--year", type=int, help="Optional year filter.")
    parser.add_argument("--language", help="Optional language filter.")
    return parser.parse_args()


def extract_article_number(query: str) -> str | None:
    match = re.search(r"(?:\u0110i\u1ec1u|Article)\s+(\d+)", query, flags=re.IGNORECASE)
    return match.group(1) if match else None


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    embedder = load_embedder_from_env(default_provider="gemini")
    store = PersistentVectorStore(
        collection_name=args.collection,
        embedding_fn=embedder,
        persist_dir=args.persist_dir,
        cache_path=args.cache_path,
    )

    metadata_filter: dict[str, object] = {}
    article_number = extract_article_number(args.query)
    if article_number:
        metadata_filter["article_number"] = article_number
    if args.domain:
        metadata_filter["domain"] = args.domain
    if args.year:
        metadata_filter["year"] = args.year
    if args.language:
        metadata_filter["language"] = args.language

    if metadata_filter:
        results = store.search_with_filter(args.query, metadata_filter=metadata_filter, top_k=args.top_k)
    else:
        results = store.search(args.query, top_k=args.top_k)

    print(f"Embedding backend: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}")
    print(f"Collection size: {store.count()}")
    if metadata_filter:
        print(f"Applied metadata filter: {metadata_filter}")

    if not results:
        print("No results.")
        return 0

    for rank, result in enumerate(results, start=1):
        preview = result["content"][:240].replace("\n", " ")
        print(
            f"Top-{rank}: score={result['score']:.4f}, "
            f"title={result['metadata'].get('document_title')}, "
            f"article={result['metadata'].get('article_number')}, "
            f"domain={result['metadata'].get('domain')}, "
            f"year={result['metadata'].get('year')}, "
            f"language={result['metadata'].get('language')}"
        )
        print(f"  preview: {preview}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
