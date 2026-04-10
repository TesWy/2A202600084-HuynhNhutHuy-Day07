import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src import (
    compute_similarity,
    load_embedder_from_env,
)


PAIRS = [
    (
        "Trí tuệ nhân tạo đang thay đổi cách chúng ta làm việc",
        "AI đang cách mạng hóa workflow hiện đại",
        "high",
    ),
    (
        "Hà Nội là thủ đô của Việt Nam",
        "Phở là món ăn truyền thống Việt Nam",
        "low",
    ),
    (
        "Máy tính lượng tử sử dụng qubit thay vì bit",
        "Quantum computer dùng qubit instead of classical bit",
        "high",
    ),
    (
        "Nhiệt độ hôm nay là 30 độ C",
        "Thời tiết nóng 30°C",
        "high",
    ),
    (
        "Chính phủ ban hành luật mới về thuế thu thập cá nhân",
        "Công ty Apple ra mắt iPhone 16",
        "low",
    ),
]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    load_dotenv(dotenv_path=Path(".env"), override=False)
    embedder = load_embedder_from_env(default_provider=os.getenv("EMBEDDING_PROVIDER", "gemini"))

    print("Similarity Predictions")
    print("=" * 80)
    print(f"Embedding backend: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}")
    print("-" * 80)

    for index, (sentence_a, sentence_b, prediction) in enumerate(PAIRS, start=1):
        vector_a = embedder(sentence_a)
        vector_b = embedder(sentence_b)
        score = compute_similarity(vector_a, vector_b)
        actual_label = "high" if score >= 0.75 else "low"

        print(f"Pair {index}")
        print(f"Sentence A : {sentence_a}")
        print(f"Sentence B : {sentence_b}")
        print(f"Prediction : {prediction}")
        print(f"Actual score: {score:.4f}")
        print(f"Actual label: {actual_label}")
        print(f"Match      : {'yes' if prediction == actual_label else 'no'}")
        print("-" * 80)


if __name__ == "__main__":
    main()
