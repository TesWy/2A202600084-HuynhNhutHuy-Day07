from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import error, parse, request

from dotenv import load_dotenv

from src import GEMINI_API_KEY_ENV, GOOGLE_API_KEY_ENV


def _load_api_key() -> str:
    load_dotenv(dotenv_path=Path(".env"), override=False)
    api_key = os.getenv(GEMINI_API_KEY_ENV) or os.getenv(GOOGLE_API_KEY_ENV)
    if not api_key:
        raise RuntimeError(
            f"Missing API key. Set {GEMINI_API_KEY_ENV} or {GOOGLE_API_KEY_ENV} in the environment or .env."
        )
    return api_key


def _fetch_all_models(api_key: str) -> list[dict]:
    models: list[dict] = []
    page_token = ""

    while True:
        params = {"key": api_key, "pageSize": "1000"}
        if page_token:
            params["pageToken"] = page_token

        url = f"https://generativelanguage.googleapis.com/v1beta/models?{parse.urlencode(params)}"
        req = request.Request(url, method="GET")

        try:
            with request.urlopen(req, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"ListModels failed with HTTP {exc.code}: {details}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"ListModels failed: {exc.reason}") from exc

        models.extend(payload.get("models", []))
        page_token = payload.get("nextPageToken", "")
        if not page_token:
            return models


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        api_key = _load_api_key()
        models = _fetch_all_models(api_key)
    except Exception as exc:
        print(str(exc))
        return 1

    embedding_models = [
        model
        for model in models
        if "embedContent" in model.get("supportedGenerationMethods", [])
    ]

    print(f"Total models returned: {len(models)}")
    print(f"Embedding-capable models: {len(embedding_models)}")
    print("-" * 80)

    for model in embedding_models:
        print(model.get("name", ""))
        print(f"  displayName: {model.get('displayName', '')}")
        print(f"  baseModelId: {model.get('baseModelId', '')}")
        print(f"  version: {model.get('version', '')}")
        print(f"  methods: {', '.join(model.get('supportedGenerationMethods', []))}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
