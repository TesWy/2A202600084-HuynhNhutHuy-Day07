from __future__ import annotations

import sys
from pathlib import Path

from src.legal_corpus import collect_legal_source_files, infer_legal_metadata


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    data_dir = Path("data").resolve()
    files = collect_legal_source_files(data_dir)

    print("| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |")
    print("|---|--------------|-------|----------|-----------------|")

    for index, path in enumerate(files, start=1):
        metadata = infer_legal_metadata(path)
        char_count = len(path.read_text(encoding="utf-8"))
        metadata_summary = (
            f"domain: {metadata['domain']}, "
            f"year: {metadata['year']}, "
            f"type: {metadata['document_type']}, "
            f"language: {metadata['language']}"
        )
        print(f"| {index} | {path.name} | data/ | {char_count:,} | {metadata_summary} |")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
