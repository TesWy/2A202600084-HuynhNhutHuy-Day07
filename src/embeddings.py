from __future__ import annotations

import hashlib
import json
import math
import os
from urllib import error, request

LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_PROVIDER_ENV = "EMBEDDING_PROVIDER"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GOOGLE_API_KEY_ENV = "GOOGLE_API_KEY"


class MockEmbedder:
    """Deterministic embedding backend used by tests and default classroom runs."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim
        self._backend_name = "mock embeddings fallback"

    def __call__(self, text: str) -> list[float]:
        digest = hashlib.md5(text.encode()).hexdigest()
        seed = int(digest, 16)
        vector = []
        for _ in range(self.dim):
            seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
            vector.append((seed / 0xFFFFFFFF) * 2 - 1)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class LocalEmbedder:
    """Sentence Transformers-backed local embedder."""

    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._backend_name = model_name
        self.model = SentenceTransformer(model_name)

    def __call__(self, text: str) -> list[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return [float(value) for value in embedding]


class OpenAIEmbedder:
    """OpenAI embeddings API-backed embedder."""

    def __init__(self, model_name: str = OPENAI_EMBEDDING_MODEL) -> None:
        from openai import OpenAI

        self.model_name = model_name
        self._backend_name = model_name
        self.client = OpenAI()

    def __call__(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model_name, input=text)
        return [float(value) for value in response.data[0].embedding]


class GeminiEmbedder:
    """Gemini embeddings via Google AI Studio API key."""

    def __init__(
        self,
        model_name: str = GEMINI_EMBEDDING_MODEL,
        api_key: str | None = None,
        task_type: str = "SEMANTIC_SIMILARITY",
    ) -> None:
        resolved_api_key = api_key or os.getenv(GEMINI_API_KEY_ENV) or os.getenv(GOOGLE_API_KEY_ENV)
        if not resolved_api_key:
            raise ValueError(
                f"GeminiEmbedder requires {GEMINI_API_KEY_ENV} or {GOOGLE_API_KEY_ENV} in the environment."
            )

        self.api_key = resolved_api_key
        self.model_name = self._normalize_model_name(model_name)
        self.task_type = task_type
        self._backend_name = self.model_name

    @staticmethod
    def _normalize_model_name(model_name: str) -> str:
        if model_name.startswith("models/"):
            return model_name
        return f"models/{model_name}"

    def __call__(self, text: str) -> list[float]:
        body: dict[str, object] = {
            "model": self.model_name,
            "content": {"parts": [{"text": text}]},
        }
        if self.task_type:
            body["taskType"] = self.task_type

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/{self.model_name}:embedContent"
        payload = json.dumps(body).encode("utf-8")
        req = request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=30) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini embeddings request failed with HTTP {exc.code}: {details}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Gemini embeddings request failed: {exc.reason}") from exc

        values = response_data.get("embedding", {}).get("values")
        if not isinstance(values, list):
            raise RuntimeError(f"Gemini embeddings response did not contain embedding values: {response_data}")

        return [float(value) for value in values]


def load_embedder_from_env(default_provider: str = "mock"):
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, default_provider).strip().lower()

    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            return _mock_embed

    if provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            return _mock_embed

    if provider in {"gemini", "google", "google_ai_studio", "aistudio"}:
        try:
            return GeminiEmbedder(model_name=os.getenv("GEMINI_EMBEDDING_MODEL", GEMINI_EMBEDDING_MODEL))
        except Exception:
            return _mock_embed

    return _mock_embed


_mock_embed = MockEmbedder()
