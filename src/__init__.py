from .agent import KnowledgeBaseAgent
from .chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    RecursiveChunker,
    SentenceChunker,
    compute_similarity,
)
from .embeddings import (
    EMBEDDING_PROVIDER_ENV,
    GEMINI_API_KEY_ENV,
    GEMINI_EMBEDDING_MODEL,
    GOOGLE_API_KEY_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    GeminiEmbedder,
    LocalEmbedder,
    MockEmbedder,
    OpenAIEmbedder,
    _mock_embed,
    load_embedder_from_env,
)
from .models import Document
from .legal_corpus import (
    ArticleChunker,
    StructuredLegalChunker,
    build_legal_chunk_documents,
    chunk_legal_text,
    collect_legal_source_files,
    extract_legal_articles,
    infer_legal_metadata,
)
from .persistent_vector_store import EmbeddingCache, PersistentVectorStore
from .store import EmbeddingStore

__all__ = [
    "Document",
    "ArticleChunker",
    "StructuredLegalChunker",
    "FixedSizeChunker",
    "SentenceChunker",
    "RecursiveChunker",
    "ChunkingStrategyComparator",
    "compute_similarity",
    "EmbeddingStore",
    "PersistentVectorStore",
    "EmbeddingCache",
    "infer_legal_metadata",
    "extract_legal_articles",
    "chunk_legal_text",
    "collect_legal_source_files",
    "build_legal_chunk_documents",
    "KnowledgeBaseAgent",
    "MockEmbedder",
    "LocalEmbedder",
    "OpenAIEmbedder",
    "GeminiEmbedder",
    "_mock_embed",
    "load_embedder_from_env",
    "LOCAL_EMBEDDING_MODEL",
    "OPENAI_EMBEDDING_MODEL",
    "GEMINI_EMBEDDING_MODEL",
    "EMBEDDING_PROVIDER_ENV",
    "GEMINI_API_KEY_ENV",
    "GOOGLE_API_KEY_ENV",
]
