from __future__ import annotations

import argparse
import re
import sys

from src import KnowledgeBaseAgent, load_embedder_from_env
from src.persistent_vector_store import PersistentVectorStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo KnowledgeBaseAgent on a persistent legal collection.")
    parser.add_argument("--collection", default="legal_full_gemini", help="Persistent collection name.")
    parser.add_argument("--persist-dir", default=".vector_store", help="Directory containing persistent store files.")
    parser.add_argument(
        "--cache-path",
        default=".vector_store/embedding_cache.json",
        help="Path for the persistent embedding cache file.",
    )
    parser.add_argument("--query", required=True, help="Question to ask the agent.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of retrieved chunks.")
    parser.add_argument("--document-title", help="Optional document_title filter.")
    parser.add_argument("--article-number", help="Optional article_number filter.")
    parser.add_argument("--domain", help="Optional domain filter.")
    parser.add_argument("--year", type=int, help="Optional year filter.")
    parser.add_argument("--language", help="Optional language filter.")
    return parser.parse_args()


def demo_llm(prompt: str) -> str:
    match = re.search(r"Context:\n(.*)\n\nQuestion:", prompt, flags=re.DOTALL)
    if not match:
        return "Tôi không có đủ thông tin trong ngữ cảnh để trả lời."

    context = match.group(1).strip()
    cleaned = re.sub(r"\[\d+\]\s*", "", context)
    cleaned = cleaned.replace("\n", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        return "Tôi không có đủ thông tin trong ngữ cảnh để trả lời."

    snippet = cleaned[:320].strip()
    return f"Dựa trên ngữ cảnh đã truy xuất: {snippet}"


class FilteredStoreAdapter:
    def __init__(self, store: PersistentVectorStore, metadata_filter: dict[str, object]) -> None:
        self.store = store
        self.metadata_filter = metadata_filter

    def search(self, query: str, top_k: int = 3):
        if self.metadata_filter:
            return self.store.search_with_filter(query, metadata_filter=self.metadata_filter, top_k=top_k)
        return self.store.search(query, top_k=top_k)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    embedder = load_embedder_from_env(default_provider="local")
    store = PersistentVectorStore(
        collection_name=args.collection,
        embedding_fn=embedder,
        persist_dir=args.persist_dir,
        cache_path=args.cache_path,
    )

    metadata_filter: dict[str, object] = {}
    if args.document_title:
        metadata_filter["document_title"] = args.document_title
    if args.article_number:
        metadata_filter["article_number"] = args.article_number
    if args.domain:
        metadata_filter["domain"] = args.domain
    if args.year:
        metadata_filter["year"] = args.year
    if args.language:
        metadata_filter["language"] = args.language

    adapter = FilteredStoreAdapter(store, metadata_filter)
    agent = KnowledgeBaseAgent(store=adapter, llm_fn=demo_llm)

    print(f"Embedding backend: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}")
    print(f"Collection size: {store.count()}")
    if metadata_filter:
        print(f"Applied metadata filter: {metadata_filter}")
    print()
    print(f"Question: {args.query}")

    retrieved = adapter.search(args.query, top_k=args.top_k)
    if not retrieved:
        print("No retrieval results.")
        return 0

    print()
    print("=== Retrieved Chunks ===")
    for rank, result in enumerate(retrieved, start=1):
        preview = result["content"][:220].replace("\n", " ")
        print(
            f"Top-{rank}: score={result['score']:.4f}, "
            f"title={result['metadata'].get('document_title')}, "
            f"article={result['metadata'].get('article_number')}, "
            f"language={result['metadata'].get('language')}"
        )
        print(f"  preview: {preview}")

    print()
    print("=== Agent Answer ===")
    print(agent.answer(args.query, top_k=args.top_k))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
