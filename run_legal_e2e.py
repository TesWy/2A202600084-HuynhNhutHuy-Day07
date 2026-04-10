from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from run_golden_queries import ensure_index, evaluate_mode, load_golden_queries, render_markdown
from src import load_embedder_from_env
from src.persistent_vector_store import PersistentVectorStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run legal indexing, golden-query evaluation, and optionally launch the UI.")
    parser.add_argument("--data-dir", default="data", help="Directory containing legal source files.")
    parser.add_argument("--collection", help="Optional persistent collection name. Auto-generated if omitted.")
    parser.add_argument("--persist-dir", default=".vector_store", help="Directory for persistent vector store files.")
    parser.add_argument(
        "--cache-path",
        default=".vector_store/embedding_cache.json",
        help="Persistent embedding cache file.",
    )
    parser.add_argument(
        "--golden-file",
        default="report/golden_queries_legal.json",
        help="JSON file containing golden queries.",
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
    parser.add_argument("--allow-mock", action="store_true", help="Allow fallback to the mock embedder.")
    parser.add_argument("--serve", action="store_true", help="Launch the local web UI after evaluation.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the local UI server.")
    parser.add_argument("--port", type=int, default=7860, help="Port for the local UI server.")
    parser.add_argument(
        "--chat-model",
        default=None,
        help="Preferred Gemini-compatible text generation model for the UI, e.g. gemma-4-31b-it.",
    )
    return parser.parse_args()


def slugify_backend(backend_name: str) -> str:
    lowered = backend_name.lower()
    if "gemini" in lowered:
        return "gemini"
    if "mock" in lowered:
        return "mock"
    if "minilm" in lowered or "sentence" in lowered:
        return "local"
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "embedder"


def resolve_collection_name(args: argparse.Namespace, backend_name: str) -> str:
    if args.collection:
        return args.collection
    return f"legal_{slugify_backend(backend_name)}_{args.strategy}_cs{args.chunk_size}"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    load_dotenv(override=False)
    args = parse_args()
    embedder = load_embedder_from_env(default_provider="local")
    backend_name = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    if "mock" in backend_name.lower() and not args.allow_mock:
        print("No real embedding backend detected. Set EMBEDDING_PROVIDER and API/model env vars, or pass --allow-mock.")
        return 1

    collection_name = resolve_collection_name(args, backend_name)
    store = PersistentVectorStore(
        collection_name=collection_name,
        embedding_fn=embedder,
        persist_dir=args.persist_dir,
        cache_path=args.cache_path,
    )

    print(f"Embedding backend: {backend_name}")
    print(f"Collection: {collection_name}")
    print(
        f"Chunking: strategy={args.strategy}, chunk_size={args.chunk_size}, "
        f"overlap={args.overlap}, max_sentences={args.max_sentences}"
    )

    data_dir = Path(args.data_dir).resolve()
    source_files, stored_chunks = ensure_index(store, args, data_dir)

    golden_queries = load_golden_queries(Path(args.golden_file).resolve())
    evaluations = [
        evaluate_mode(store, golden_queries, args.top_k, mode="no_filter"),
        evaluate_mode(store, golden_queries, args.top_k, mode="gold_filter"),
    ]

    output_md = Path("report") / f"{collection_name}_golden_results.md"
    output_json = Path("report") / f"{collection_name}_golden_results.json"

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "embedding_backend": backend_name,
        "collection": collection_name,
        "strategy": args.strategy,
        "parameters": {
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "max_sentences": args.max_sentences,
            "top_k": args.top_k,
        },
        "source_files": source_files,
        "stored_chunks": stored_chunks,
        "golden_file": str(Path(args.golden_file).resolve()),
        "evaluations": evaluations,
    }

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    for evaluation in evaluations:
        summary = evaluation["summary"]
        print(
            f"Mode={summary['mode']}: top1_exact_rate={summary['top1_exact_rate']}, "
            f"top3_exact_rate={summary['top3_exact_rate']}, pass_rate={summary['pass_rate']}, "
            f"avg_keyword_recall={summary['avg_keyword_recall']}"
        )
    print(f"Markdown report: {output_md.resolve()}")
    print(f"JSON report: {output_json.resolve()}")

    if args.serve:
        print()
        print(f"Launching UI at http://{args.host}:{args.port}")
        from run_legal_agent_ui import create_app

        app = create_app(collection_name, args.persist_dir, args.cache_path, preferred_chat_model=args.chat_model)
        app.run(host=args.host, port=args.port, debug=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
