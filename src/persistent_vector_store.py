from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from .chunking import _dot
from .models import Document


def _hash_key(parts: list[str]) -> str:
    joined = "\n".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


class EmbeddingCache:
    """Simple JSON-backed embedding cache keyed by backend name and text hash."""

    def __init__(self, cache_path: str | Path, auto_flush_every: int = 64) -> None:
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.auto_flush_every = max(1, auto_flush_every)
        if self.cache_path.exists():
            self._cache: dict[str, list[float]] = json.loads(self.cache_path.read_text(encoding="utf-8"))
        else:
            self._cache = {}
        self._dirty = False
        self._pending_writes = 0

    def _make_key(self, backend_name: str, text: str) -> str:
        return _hash_key([backend_name, text])

    def get(self, backend_name: str, text: str) -> list[float] | None:
        return self._cache.get(self._make_key(backend_name, text))

    def set(self, backend_name: str, text: str, embedding: list[float], flush: bool = False) -> None:
        self._cache[self._make_key(backend_name, text)] = embedding
        self._dirty = True
        self._pending_writes += 1
        if flush or self._pending_writes >= self.auto_flush_every:
            self.flush()

    def flush(self) -> None:
        if not self._dirty:
            return
        self.cache_path.write_text(json.dumps(self._cache, ensure_ascii=False), encoding="utf-8")
        self._dirty = False
        self._pending_writes = 0

    def embed(self, embedding_fn: Callable[[str], list[float]], backend_name: str, text: str) -> list[float]:
        embedding, _ = self.embed_with_status(embedding_fn, backend_name, text)
        return embedding

    def embed_with_status(
        self,
        embedding_fn: Callable[[str], list[float]],
        backend_name: str,
        text: str,
    ) -> tuple[list[float], bool]:
        cached = self.get(backend_name, text)
        if cached is not None:
            return cached, True
        embedding = embedding_fn(text)
        self.set(backend_name, text, embedding)
        return embedding, False


class PersistentVectorStore:
    """Disk-backed vector store for experiments, separate from the grading store."""

    def __init__(
        self,
        collection_name: str,
        embedding_fn: Callable[[str], list[float]],
        persist_dir: str | Path = ".vector_store",
        cache_path: str | Path = ".vector_store/embedding_cache.json",
        cache_flush_every: int = 64,
    ) -> None:
        self.collection_name = collection_name
        self.embedding_fn = embedding_fn
        self.backend_name = getattr(embedding_fn, "_backend_name", embedding_fn.__class__.__name__)
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_path = self.persist_dir / f"{collection_name}.json"
        self.cache = EmbeddingCache(cache_path, auto_flush_every=cache_flush_every)

        if self.collection_path.exists():
            self.records: list[dict[str, Any]] = json.loads(self.collection_path.read_text(encoding="utf-8"))
        else:
            self.records = []

    def _save(self) -> None:
        self.collection_path.write_text(json.dumps(self.records, ensure_ascii=False), encoding="utf-8")

    def clear(self) -> None:
        self.records = []
        self._save()

    def count(self) -> int:
        return len(self.records)

    def remove_document(self, doc_id: str) -> int:
        before = len(self.records)
        self.records = [record for record in self.records if record["metadata"].get("doc_id") != doc_id]
        removed = before - len(self.records)
        if removed:
            self._save()
        return removed

    def add_documents(
        self,
        docs: list[Document],
        replace_doc_ids: bool = False,
        progress_callback: Callable[[dict[str, int]], None] | None = None,
        progress_every: int = 50,
    ) -> dict[str, int]:
        if replace_doc_ids:
            for doc_id in sorted({doc.id for doc in docs}):
                self.remove_document(doc_id)

        start_index = len(self.records)
        cache_hits = 0
        cache_misses = 0
        total = len(docs)
        progress_every = max(1, progress_every)

        for offset, doc in enumerate(docs, start=1):
            embedding, cache_hit = self.cache.embed_with_status(self.embedding_fn, self.backend_name, doc.content)
            if cache_hit:
                cache_hits += 1
            else:
                cache_misses += 1
            self.records.append(
                {
                    "id": f"{self.collection_name}_{start_index + offset - 1}",
                    "content": doc.content,
                    "embedding": embedding,
                    "metadata": {
                        "doc_id": doc.id,
                        **(doc.metadata or {}),
                    },
                }
            )
            if progress_callback and (offset == 1 or offset == total or offset % progress_every == 0):
                progress_callback(
                    {
                        "processed": offset,
                        "total": total,
                        "cache_hits": cache_hits,
                        "cache_misses": cache_misses,
                    }
                )

        self.cache.flush()
        self._save()
        return {
            "added": total,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_embedding = self.cache.embed(self.embedding_fn, self.backend_name, query)
        self.cache.flush()

        scored = []
        for record in records:
            scored.append((_dot(query_embedding, record["embedding"]), record))

        scored.sort(key=lambda item: item[0], reverse=True)

        results: list[dict[str, Any]] = []
        for score, record in scored[:top_k]:
            result = dict(record)
            result["score"] = score
            results.append(result)
        return results

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self._search_records(query, self.records, top_k)

    def search_with_filter(self, query: str, metadata_filter: dict[str, object], top_k: int = 5) -> list[dict[str, Any]]:
        filtered = [
            record
            for record in self.records
            if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, filtered, top_k)
