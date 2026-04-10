from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from src import (
    ChunkingStrategyComparator,
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    RecursiveChunker,
    SentenceChunker,
    load_embedder_from_env,
)


DEFAULT_QUERIES = [
    "Điều 1 quy định phạm vi điều chỉnh của Bộ luật dân sự 2015 là gì?",
    "Điều 3 nêu các nguyên tắc cơ bản của pháp luật dân sự như thế nào?",
    "Điều 11 quy định các phương thức bảo vệ quyền dân sự là gì?",
    "Điều 16 quy định năng lực pháp luật dân sự của cá nhân như thế nào?",
    "Điều 74 quy định điều kiện để một tổ chức được công nhận là pháp nhân là gì?",
]


def extract_article_number(query: str) -> str | None:
    match = re.search(r"Điều\s+(\d+)", query, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1)


def build_demo_answer_from_results(results: list[dict]) -> str:
    if not results:
        return "No retrieved context."

    top_result = results[0]
    lines = [line.strip() for line in top_result["content"].splitlines() if line.strip()]
    summary = " ".join(lines[:3])
    return summary[:240]


class ArticleChunker:
    """Chunk legal text by article headings such as 'Điều 1.'."""

    ARTICLE_PATTERN = re.compile(r"(?=^Điều\s+\d+\.)", flags=re.MULTILINE)

    def chunk(self, text: str) -> list[str]:
        start_match = re.search(r"^Điều\s+1\.", text, flags=re.MULTILINE)
        working_text = text[start_match.start() :] if start_match else text

        parts = [part.strip() for part in self.ARTICLE_PATTERN.split(working_text) if part.strip()]
        return parts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run chunking and retrieval experiments on a single document.")
    parser.add_argument("file", help="Path to a .txt or .md document.")
    parser.add_argument(
        "--strategy",
        choices=["fixed", "sentences", "recursive", "articles"],
        default="articles",
        help="Chunking strategy for retrieval. Default: articles",
    )
    parser.add_argument("--chunk-size", type=int, default=1000, help="Chunk size for fixed/recursive. Default: 1000")
    parser.add_argument(
        "--overlap",
        type=int,
        default=100,
        help="Overlap for fixed-size chunking. Default: 100",
    )
    parser.add_argument(
        "--max-sentences",
        type=int,
        default=3,
        help="Max sentences per chunk for sentence chunking. Default: 3",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top retrieved chunks to display. Default: 3",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=0,
        help="Optionally limit how many chunks are embedded for quick experiments. 0 means no limit.",
    )
    parser.add_argument(
        "--query",
        action="append",
        dest="queries",
        help="Benchmark query. Repeat this flag to add multiple queries.",
    )
    return parser.parse_args()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_chunker(args: argparse.Namespace):
    if args.strategy == "fixed":
        return FixedSizeChunker(chunk_size=args.chunk_size, overlap=args.overlap)
    if args.strategy == "sentences":
        return SentenceChunker(max_sentences_per_chunk=args.max_sentences)
    if args.strategy == "articles":
        return ArticleChunker()
    return RecursiveChunker(chunk_size=args.chunk_size)


def build_chunk_documents(source_path: Path, chunks: list[str]) -> list[Document]:
    documents: list[Document] = []
    for index, chunk in enumerate(chunks):
        first_line = chunk.splitlines()[0].strip() if chunk.strip() else ""
        article_match = re.match(r"^Điều\s+(\d+)\.\s*(.*)$", first_line)
        documents.append(
            Document(
                id=f"{source_path.stem}_chunk_{index}",
                content=chunk,
                metadata={
                    "source": source_path.name,
                    "category": "law",
                    "language": "vi",
                    "chunk_index": index,
                    "article_number": article_match.group(1) if article_match else "",
                    "article_title": article_match.group(2) if article_match else "",
                },
            )
        )
    return documents


def print_comparator_stats(text: str, chunk_size: int) -> None:
    result = ChunkingStrategyComparator().compare(text, chunk_size=chunk_size)
    print("=== Chunking Comparison ===")
    for name, stats in result.items():
        print(
            f"{name}: count={stats['count']}, avg_length={stats['avg_length']}, "
            f"sample_preview={repr(stats['chunks'][0][:120]) if stats['chunks'] else ''}"
        )
    print()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    source_path = Path(args.file).expanduser().resolve()
    if not source_path.exists():
        print(f"File not found: {source_path}")
        return 1

    text = load_text(source_path)
    queries = args.queries or DEFAULT_QUERIES

    print_comparator_stats(text, chunk_size=args.chunk_size)

    chunker = build_chunker(args)
    chunks = chunker.chunk(text)
    if args.max_chunks and args.max_chunks > 0:
        chunks = chunks[: args.max_chunks]
    docs = build_chunk_documents(source_path, chunks)
    embedder = load_embedder_from_env(default_provider="gemini")
    store = EmbeddingStore(collection_name=f"{source_path.stem}_experiment", embedding_fn=embedder)

    backend_name = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    print("=== Retrieval Setup ===")
    print(f"Embedding backend: {backend_name}")
    print(f"Strategy: {args.strategy}")
    print(f"Chunks prepared: {len(chunks)}")
    if len(chunks) >= 1000 and "mock" not in backend_name.lower():
        print("Warning: chunk count is very high for a remote embedding API. Use --max-chunks or a larger chunk size.")
    print("Embedding and storing chunks...")

    for index, doc in enumerate(docs, start=1):
        store.add_documents([doc])
        if index == 1 or index % 50 == 0 or index == len(docs):
            print(f"  stored {index}/{len(docs)} chunks")

    print(f"Chunks stored: {store.get_collection_size()}")
    print()

    print("=== Benchmark Queries ===")
    for index, query in enumerate(queries, start=1):
        article_number = extract_article_number(query)
        metadata_filter = {"article_number": article_number} if article_number else None
        if metadata_filter:
            results = store.search_with_filter(query, top_k=args.top_k, metadata_filter=metadata_filter)
        else:
            results = store.search(query, top_k=args.top_k)
        answer = build_demo_answer_from_results(results)

        print(f"Query {index}: {query}")
        if metadata_filter:
            print(f"  Applied metadata filter: {metadata_filter}")
        if not results:
            print("  No retrieval results.")
            print()
            continue

        for rank, result in enumerate(results, start=1):
            preview = result["content"][:180].replace("\n", " ")
            article_number = result["metadata"].get("article_number")
            article_title = result["metadata"].get("article_title")
            article_info = f", article={article_number}" if article_number else ""
            if article_title:
                article_info += f" ({article_title})"
            print(
                f"  Top-{rank}: score={result['score']:.4f}, "
                f"chunk_index={result['metadata'].get('chunk_index')}{article_info}, preview={preview}"
            )

        print(f"  Agent answer: {answer[:180]}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
