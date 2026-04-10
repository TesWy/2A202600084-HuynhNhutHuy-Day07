from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib import error, request

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request as flask_request

from src import KnowledgeBaseAgent, load_embedder_from_env
from src.persistent_vector_store import PersistentVectorStore

GEMINI_CHAT_MODEL_ENV = "GEMINI_CHAT_MODEL"
DEFAULT_CHAT_MODELS = ["gemma-4-31b-it", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


class FilteredStoreAdapter:
    def __init__(self, store: PersistentVectorStore, metadata_filter: dict[str, object]) -> None:
        self.store = store
        self.metadata_filter = metadata_filter

    def search(self, query: str, top_k: int = 3):
        if self.metadata_filter:
            return self.store.search_with_filter(query, metadata_filter=self.metadata_filter, top_k=top_k)
        return self.store.search(query, top_k=top_k)


class PersistentStoreRegistry:
    def __init__(self, embedder, persist_dir: str | Path, cache_path: str | Path) -> None:
        self.embedder = embedder
        self.persist_dir = Path(persist_dir)
        self.cache_path = Path(cache_path)
        self._stores: dict[str, tuple[float, PersistentVectorStore]] = {}

    def list_collections(self) -> list[str]:
        return sorted(path.stem for path in self.persist_dir.glob("*.json"))

    def get(self, collection_name: str) -> PersistentVectorStore:
        collection_path = self.persist_dir / f"{collection_name}.json"
        if not collection_path.exists():
            raise FileNotFoundError(f"Collection not found: {collection_name}")

        mtime = collection_path.stat().st_mtime
        cached = self._stores.get(collection_name)
        if cached and cached[0] == mtime:
            return cached[1]

        store = PersistentVectorStore(
            collection_name=collection_name,
            embedding_fn=self.embedder,
            persist_dir=self.persist_dir,
            cache_path=self.cache_path,
        )
        self._stores[collection_name] = (mtime, store)
        return store


class GeminiChatResponder:
    def __init__(self, api_key: str | None = None, preferred_model: str | None = None) -> None:
        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.api_key = resolved_api_key
        self.models = self._candidate_models(preferred_model or os.getenv(GEMINI_CHAT_MODEL_ENV))

    @staticmethod
    def _candidate_models(preferred: str | None) -> list[str]:
        ordered: list[str] = []
        for model_name in [preferred, *DEFAULT_CHAT_MODELS]:
            if not model_name:
                continue
            normalized = model_name if model_name.startswith("models/") else f"models/{model_name}"
            if normalized not in ordered:
                ordered.append(normalized)
        return ordered

    def available(self) -> bool:
        return bool(self.api_key)

    def describe(self) -> str:
        if not self.available():
            return "extractive fallback"
        return self.models[0] if self.models else "gemini"

    def __call__(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini API key not found in environment.")

        last_error: Exception | None = None
        for model_name in self.models:
            try:
                return self._generate(model_name, prompt)
            except Exception as exc:  # pragma: no cover - non-critical fallback path
                last_error = exc
        raise RuntimeError(f"Gemini text generation failed for all candidate models: {last_error}") from last_error

    def _generate(self, model_name: str, prompt: str) -> str:
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.15,
                "maxOutputTokens": 220,
                "topP": 0.9,
            },
        }

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent"
        req = request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini generateContent failed with HTTP {exc.code}: {details}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Gemini generateContent failed: {exc.reason}") from exc

        candidates = payload.get("candidates") or []
        if not candidates:
            raise RuntimeError(f"Gemini response did not return candidates: {payload}")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
        if not text:
            raise RuntimeError(f"Gemini response did not contain text: {payload}")
        return normalize_agent_answer(text)


def normalize_agent_answer(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return cleaned

    marker = "FINAL_ANSWER:"
    if marker in cleaned:
        cleaned = cleaned.rsplit(marker, maxsplit=1)[-1].strip()

    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n").strip()

    # Standardize "not enough information" replies even when the model wraps them in analysis.
    insufficient_patterns = [
        r"I don't have enough information\.?",
        r"Tôi không có đủ thông tin(?: trong ngữ cảnh)?(?: để trả lời)?\.?",
    ]
    for pattern in insufficient_patterns:
        matches = list(re.finditer(pattern, cleaned, flags=re.IGNORECASE))
        if not matches:
            continue
        last_match = matches[-1]
        trailing = cleaned[last_match.start() :].strip()
        if len(trailing) <= 160:
            return "Tôi không có đủ thông tin trong ngữ cảnh để trả lời."

    cleaned = _extract_last_answer_block(cleaned)
    cleaned = _strip_meta_lines(cleaned)
    cleaned = _shorten_answer(cleaned)
    return cleaned or "Tôi không có đủ thông tin trong ngữ cảnh để trả lời."


def _looks_like_meta_line(line: str) -> bool:
    normalized = line.strip().lstrip("*-• ").strip().lower()
    if not normalized:
        return False

    meta_prefixes = (
        "context:",
        "question:",
        "constraint:",
        "draft",
        "drafting",
        "the question asks",
        "the provided text",
        "the provided context",
        "does it use only the context",
        "does it answer the question",
        "since the context",
        "let's provide",
        "answer based",
    )
    return normalized.startswith(meta_prefixes)


def _extract_last_answer_block(text: str) -> str:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    if not blocks:
        return text.strip()

    cue_patterns = [
        r"^dựa trên\b",
        r"^theo\b",
        r"^luật .+ quy định",
        r"^nội dung chính",
        r"^trả lời\b",
        r"^\d+\.\s",
        r"^[-*•]\s",
    ]

    for block in reversed(blocks):
        first_line = block.splitlines()[0].strip()
        if _looks_like_meta_line(first_line):
            continue
        if any(re.match(pattern, first_line, flags=re.IGNORECASE) for pattern in cue_patterns):
            return block

    for block in reversed(blocks):
        first_line = block.splitlines()[0].strip()
        if not _looks_like_meta_line(first_line):
            return block

    return blocks[-1]


def _strip_meta_lines(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    filtered_lines: list[str] = []
    for line in lines:
        if _looks_like_meta_line(line):
            continue
        filtered_lines.append(line.strip())
    cleaned = "\n".join(line for line in filtered_lines if line).strip()
    return re.sub(r"\n{3,}", "\n\n", cleaned)


def _shorten_answer(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    bullet_lines = [line for line in lines if re.match(r"^(\d+\.|[-*•])\s+", line)]

    if bullet_lines:
        intro = []
        if lines and lines[0] not in bullet_lines:
            intro = [lines[0]]
        return "\n".join(intro + bullet_lines[:4]).strip()

    sentences = re.split(r"(?<=[.!?])\s+", stripped)
    limited = " ".join(sentence.strip() for sentence in sentences[:3] if sentence.strip()).strip()
    words = limited.split()
    if len(words) > 120:
        limited = " ".join(words[:120]).strip()
    return limited or stripped


def extractive_fallback(prompt: str) -> str:
    context_match = re.search(r"Context:\n(.*)\n\nQuestion:", prompt, flags=re.DOTALL)
    if not context_match:
        return "Tôi không có đủ thông tin trong ngữ cảnh để trả lời."

    question_match = re.search(r"Question:\s*(.*)\n\nAnswer:", prompt, flags=re.DOTALL)
    question = question_match.group(1).strip() if question_match else ""
    context = context_match.group(1)
    cleaned = re.sub(r"\[\d+\]\s*", "", context)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return "Tôi không có đủ thông tin trong ngữ cảnh để trả lời."

    snippet = cleaned[:320].strip()
    return normalize_agent_answer(f"FINAL_ANSWER:\n{snippet}")


def build_metadata_filter(payload: dict[str, Any]) -> dict[str, object]:
    filter_map: dict[str, object] = {}
    for key in ["document_title", "article_number", "domain", "language"]:
        value = str(payload.get(key) or "").strip()
        if value:
            filter_map[key] = value

    year = payload.get("year")
    if year not in (None, "", "null"):
        try:
            filter_map["year"] = int(year)
        except ValueError:
            pass
    return filter_map


def summarize_store_metadata(store: PersistentVectorStore) -> dict[str, Any]:
    records = store.records
    titles = sorted({str(record["metadata"].get("document_title")) for record in records if record["metadata"].get("document_title")})
    domains = sorted({str(record["metadata"].get("domain")) for record in records if record["metadata"].get("domain")})
    languages = sorted({str(record["metadata"].get("language")) for record in records if record["metadata"].get("language")})
    years = sorted({int(record["metadata"].get("year")) for record in records if record["metadata"].get("year") is not None})
    return {
        "count": len(records),
        "titles": titles,
        "domains": domains,
        "languages": languages,
        "years": years,
    }


def suggested_questions() -> list[str]:
    return [
        "Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân?",
        "Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì?",
        "When is Vietnam's Population Day?",
        "Name three banned business lines under the Law on Investment 2025.",
        "In the Planning Law 2025, what is the national planning database?",
    ]


def api_error(message: str, status_code: int = 500):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


def compute_asset_version(static_dir: Path) -> str:
    asset_names = ["legal_agent_ui.css", "legal_agent_ui.js"]
    mtimes: list[str] = []
    for name in asset_names:
        asset_path = static_dir / name
        if asset_path.exists():
            mtimes.append(str(int(asset_path.stat().st_mtime)))
    return "-".join(mtimes) or "dev"


def create_app(
    default_collection: str,
    persist_dir: str,
    cache_path: str,
    preferred_chat_model: str | None = None,
) -> Flask:
    load_dotenv(override=False)
    embedder = load_embedder_from_env(default_provider="local")
    responder = GeminiChatResponder(preferred_model=preferred_chat_model)
    registry = PersistentStoreRegistry(embedder=embedder, persist_dir=persist_dir, cache_path=cache_path)

    app = Flask(
        __name__,
        template_folder=str(Path(__file__).with_name("templates")),
        static_folder=str(Path(__file__).with_name("static")),
    )
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    static_dir = Path(app.static_folder or Path(__file__).with_name("static"))
    asset_version = compute_asset_version(static_dir)

    @app.after_request
    def apply_no_cache_headers(response):
        if flask_request.path == "/" or flask_request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    @app.get("/")
    def index():
        collections = registry.list_collections()
        chosen_collection = default_collection if default_collection in collections else (collections[0] if collections else "")
        if chosen_collection:
            try:
                initial_summary = summarize_store_metadata(registry.get(chosen_collection))
            except FileNotFoundError:
                initial_summary = {"count": 0, "titles": [], "domains": [], "languages": [], "years": []}
        else:
            initial_summary = {"count": 0, "titles": [], "domains": [], "languages": [], "years": []}
        return render_template(
            "legal_agent_ui.html",
            collections=collections,
            default_collection=chosen_collection,
            default_backend=getattr(embedder, "_backend_name", embedder.__class__.__name__),
            generation_mode=responder.describe(),
            suggested_questions=suggested_questions(),
            initial_summary=initial_summary,
            asset_version=asset_version,
        )

    @app.get("/api/state")
    def state():
        try:
            collection = flask_request.args.get("collection", default_collection)
            store = registry.get(collection)
            return jsonify(
                {
                    "collection": collection,
                    "embedding_backend": getattr(embedder, "_backend_name", embedder.__class__.__name__),
                    "generation_mode": responder.describe(),
                    "summary": summarize_store_metadata(store),
                }
            )
        except FileNotFoundError as exc:
            return api_error(str(exc), status_code=404)
        except Exception as exc:
            return api_error(f"State endpoint failed: {exc}", status_code=500)

    @app.post("/api/ask")
    def ask():
        try:
            payload = flask_request.get_json(silent=True) or {}
            collection = str(payload.get("collection") or default_collection)
            question = str(payload.get("query") or "").strip()
            top_k = int(payload.get("top_k") or 3)

            if not question:
                return api_error("Query is required.", status_code=400)

            store = registry.get(collection)
            metadata_filter = build_metadata_filter(payload)
            adapter = FilteredStoreAdapter(store, metadata_filter)

            llm_fn = responder if responder.available() else extractive_fallback
            agent = KnowledgeBaseAgent(store=adapter, llm_fn=llm_fn)

            sources = adapter.search(question, top_k=top_k)
            generation_mode = responder.describe()
            warning = ""
            try:
                answer = agent.answer(question, top_k=top_k)
            except RuntimeError as exc:
                fallback_agent = KnowledgeBaseAgent(store=adapter, llm_fn=extractive_fallback)
                answer = fallback_agent.answer(question, top_k=top_k)
                generation_mode = "extractive fallback"
                warning = f"Gemini chat failed, fallback applied: {exc}"
            answer = normalize_agent_answer(answer)
            return jsonify(
                {
                    "collection": collection,
                    "question": question,
                    "answer": answer,
                    "embedding_backend": getattr(embedder, "_backend_name", embedder.__class__.__name__),
                    "generation_mode": generation_mode,
                    "metadata_filter": metadata_filter,
                    "warning": warning,
                    "sources": [
                        {
                            "rank": index,
                            "score": result["score"],
                            "content": result["content"],
                            "preview": result["content"][:320].replace("\n", " "),
                            "metadata": result["metadata"],
                        }
                        for index, result in enumerate(sources, start=1)
                    ],
                }
            )
        except FileNotFoundError as exc:
            return api_error(str(exc), status_code=404)
        except Exception as exc:
            return api_error(f"Ask endpoint failed: {exc}", status_code=500)

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the interactive legal agent web UI.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the web server.")
    parser.add_argument("--port", type=int, default=7860, help="Port to bind the web server.")
    parser.add_argument("--collection", default="legal_full_gemini", help="Default collection for the UI.")
    parser.add_argument(
        "--chat-model",
        default=None,
        help="Preferred Gemini-compatible text generation model, e.g. gemma-4-31b-it.",
    )
    parser.add_argument("--persist-dir", default=".vector_store", help="Directory containing persistent collections.")
    parser.add_argument(
        "--cache-path",
        default=".vector_store/embedding_cache.json",
        help="Path to the persistent embedding cache file.",
    )
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = create_app(
        default_collection=args.collection,
        persist_dir=args.persist_dir,
        cache_path=args.cache_path,
        preferred_chat_model=args.chat_model,
    )
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
