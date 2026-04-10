from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from pypdf import PdfReader


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pages(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        raw_text = page.extract_text() or ""
        pages.append(normalize_text(raw_text))
    return pages


def pages_to_txt(pages: list[str]) -> str:
    sections: list[str] = []
    for index, page_text in enumerate(pages, start=1):
        sections.append(f"===== Page {index} =====")
        sections.append(page_text)
    return "\n\n".join(sections).strip() + "\n"


def pages_to_markdown(pages: list[str], source_name: str) -> str:
    sections = [f"# {source_name}", ""]
    for index, page_text in enumerate(pages, start=1):
        sections.append(f"## Page {index}")
        sections.append("")
        sections.append(page_text if page_text else "_No extractable text on this page._")
        sections.append("")
    return "\n".join(sections).strip() + "\n"


def convert_pdf(pdf_path: Path, output_format: str) -> str:
    pages = extract_pages(pdf_path)
    if output_format == "txt":
        return pages_to_txt(pages)
    if output_format == "md":
        return pages_to_markdown(pages, pdf_path.stem)
    raise ValueError(f"Unsupported format: {output_format}")


def resolve_inputs(input_path: Path, recursive: bool) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        pattern = "**/*.pdf" if recursive else "*.pdf"
        return sorted(path for path in input_path.glob(pattern) if path.is_file())
    raise FileNotFoundError(f"Input path not found: {input_path}")


def build_output_path(pdf_path: Path, output_target: Path | None, output_format: str, single_input: bool) -> Path:
    suffix = ".md" if output_format == "md" else ".txt"
    if output_target is None:
        return pdf_path.with_suffix(suffix)

    if single_input and (not output_target.exists() or output_target.suffix.lower() in {".md", ".txt"}):
        return output_target

    output_target.mkdir(parents=True, exist_ok=True)
    return output_target / f"{pdf_path.stem}{suffix}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert one PDF or a directory of PDFs into Markdown or plain text."
    )
    parser.add_argument("input", help="Path to a PDF file or a directory containing PDFs.")
    parser.add_argument(
        "--format",
        choices=["md", "txt"],
        default="txt",
        help="Output format. Default: txt",
    )
    parser.add_argument(
        "--output",
        help="Output file path for a single PDF, or output directory for multiple PDFs.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search for PDFs when the input path is a directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output files.",
    )
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_target = Path(args.output).expanduser().resolve() if args.output else None

    try:
        pdf_paths = resolve_inputs(input_path, recursive=args.recursive)
    except Exception as exc:
        print(str(exc))
        return 1

    if not pdf_paths:
        print(f"No PDF files found under {input_path}")
        return 1

    single_input = len(pdf_paths) == 1
    for pdf_path in pdf_paths:
        try:
            content = convert_pdf(pdf_path, args.format)
            output_path = build_output_path(pdf_path, output_target, args.format, single_input)
            if output_path.exists() and not args.force:
                print(f"Skip existing file: {output_path}")
                continue

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            print(f"Converted: {pdf_path.name} -> {output_path}")
        except Exception as exc:
            print(f"Failed: {pdf_path} ({exc})")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
