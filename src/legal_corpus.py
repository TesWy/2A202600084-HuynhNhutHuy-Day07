from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from .models import Document

VI_ARTICLE_WORD = "\u0110i\u1ec1u"
VI_CHAPTER_WORD = "Ch\u01b0\u01a1ng"
VI_PART_WORD = "Ph\u1ea7n"
VI_SECTION_WORD = "M\u1ee5c"

YEAR_PATTERN = re.compile(r"(19|20)\d{2}")
CLAUSE_PATTERN = re.compile(r"^\d+\.\s+")
LETTER_CLAUSE_PATTERN = re.compile(r"^[a-z]\)\s+", flags=re.IGNORECASE)

ARTICLE_HEADER_PATTERNS = [
    (
        "vi",
        re.compile(
            rf"^(?P<label>{VI_ARTICLE_WORD}\s+(?P<number>\d+)[\.\-:]?\s*(?P<title>.*))$"
        ),
    ),
    (
        "en",
        re.compile(r"^(?P<label>Article\s+(?P<number>\d+)[\.\-:]?\s*(?P<title>.*))$", flags=re.IGNORECASE),
    ),
]

STRUCTURE_PATTERNS = [
    ("part", re.compile(rf"^(?P<label>{VI_PART_WORD}\s+.+)$", flags=re.IGNORECASE)),
    ("part", re.compile(r"^(?P<label>Part\s+[A-Z0-9IVXLCM]+(?:\.\s*.*)?)$", flags=re.IGNORECASE)),
    ("chapter", re.compile(rf"^(?P<label>{VI_CHAPTER_WORD}\s+.+)$", flags=re.IGNORECASE)),
    ("chapter", re.compile(r"^(?P<label>Chapter\s+[A-Z0-9IVXLCM]+(?:\.\s*.*)?)$", flags=re.IGNORECASE)),
    ("section", re.compile(rf"^(?P<label>{VI_SECTION_WORD}\s+.+)$", flags=re.IGNORECASE)),
    ("section", re.compile(r"^(?P<label>Section\s+\d+(?:\.\s*.*)?)$", flags=re.IGNORECASE)),
]

FIRST_ARTICLE_PATTERN = re.compile(
    rf"(?m)^(?:{VI_ARTICLE_WORD}|Article)\s+\d+\b",
    flags=re.IGNORECASE,
)

DOMAIN_RULES = [
    ("educator", "Gi\u00e1o d\u1ee5c"),
    ("education", "Gi\u00e1o d\u1ee5c"),
    ("investment", "Kinh t\u1ebf"),
    ("planning", "Kinh t\u1ebf"),
    ("population", "X\u00e3 h\u1ed9i"),
    ("children", "X\u00e3 h\u1ed9i"),
    ("press", "X\u00e3 h\u1ed9i"),
    ("marriage", "D\u00e2n s\u1ef1"),
    ("family", "D\u00e2n s\u1ef1"),
    ("civil", "D\u00e2n s\u1ef1"),
    ("d\u00e2n s\u1ef1", "D\u00e2n s\u1ef1"),
]


@dataclass
class LegalChunk:
    content: str
    metadata: dict[str, object]


def normalize_legal_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\ufeff", "")
    return normalized.replace("\xa0", " ")


def trim_to_first_article(text: str) -> str:
    normalized = normalize_legal_text(text)
    match = FIRST_ARTICLE_PATTERN.search(normalized)
    if not match:
        return normalized.strip()
    return normalized[match.start() :].strip()


def detect_language(path: Path, text: str) -> str:
    stem_lower = path.stem.lower()
    normalized = normalize_legal_text(text)

    if re.search(r"(?m)^Article\s+\d+\b", normalized, flags=re.IGNORECASE):
        return "en"
    if re.search(rf"(?m)^{VI_ARTICLE_WORD}\s+\d+\b", normalized):
        return "vi"
    if any(keyword in stem_lower for keyword in ["law", "children", "planning", "population", "investment"]):
        return "en"
    if any(keyword in stem_lower for keyword in ["lu\u1eadt", "b\u1ed9 lu\u1eadt", "ngh\u1ecb quy\u1ebft"]):
        return "vi"
    return "unknown"


def _match_article_header(line: str) -> dict[str, str] | None:
    stripped = line.strip()
    for language, pattern in ARTICLE_HEADER_PATTERNS:
        match = pattern.match(stripped)
        if match:
            return {
                "language": language,
                "label": match.group("label").strip(),
                "number": match.group("number").strip(),
                "title": match.group("title").strip(),
            }
    return None


def parse_article_header(chunk: str) -> tuple[str, str]:
    first_line = chunk.splitlines()[0].strip() if chunk.strip() else ""
    match = _match_article_header(first_line)
    if not match:
        return "", ""
    return match["number"], match["title"]


def _match_structure_heading(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    for kind, pattern in STRUCTURE_PATTERNS:
        match = pattern.match(stripped)
        if match:
            return kind, match.group("label").strip()
    return None


def _is_heading_title(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 120:
        return False
    if _match_article_header(stripped) or _match_structure_heading(stripped):
        return False
    letters = [char for char in stripped if char.isalpha()]
    if not letters:
        return False
    uppercase_ratio = sum(1 for char in letters if char.isupper()) / len(letters)
    return uppercase_ratio >= 0.7


def _consume_heading_with_optional_title(lines: list[str], index: int, label: str) -> tuple[str, int]:
    next_index = index + 1
    while next_index < len(lines) and not lines[next_index].strip():
        next_index += 1
    if next_index >= len(lines):
        return label, index

    candidate = lines[next_index].strip()
    if _is_heading_title(candidate):
        return f"{label} | {candidate}", next_index
    return label, index


def extract_legal_articles(text: str) -> list[dict[str, object]]:
    lines = normalize_legal_text(text).split("\n")
    context = {"part_label": "", "chapter_label": "", "section_label": ""}
    articles: list[dict[str, object]] = []
    current_lines: list[str] = []
    current_metadata: dict[str, object] = {}

    index = 0
    while index < len(lines):
        raw_line = lines[index].rstrip()
        stripped = raw_line.strip()

        if not stripped:
            if current_lines and current_lines[-1] != "":
                current_lines.append("")
            index += 1
            continue

        structure = _match_structure_heading(stripped)
        if structure:
            kind, label = structure
            combined_label, consumed_index = _consume_heading_with_optional_title(lines, index, label)
            if kind == "part":
                context["part_label"] = combined_label
                context["chapter_label"] = ""
                context["section_label"] = ""
            elif kind == "chapter":
                context["chapter_label"] = combined_label
                context["section_label"] = ""
            else:
                context["section_label"] = combined_label
            index = consumed_index + 1
            continue

        article_match = _match_article_header(stripped)
        if article_match:
            if current_lines:
                articles.append(
                    {
                        "content": "\n".join(current_lines).strip(),
                        **current_metadata,
                    }
                )
            current_lines = [stripped]
            current_metadata = {
                **context,
                "article_number": article_match["number"],
                "article_title": article_match["title"],
                "article_label": article_match["label"],
                "article_language": article_match["language"],
            }
            index += 1
            continue

        if current_lines:
            current_lines.append(raw_line)

        index += 1

    if current_lines:
        articles.append(
            {
                "content": "\n".join(current_lines).strip(),
                **current_metadata,
            }
        )

    return articles


def _split_article_units(article_text: str) -> tuple[str, list[str]]:
    lines = article_text.splitlines()
    if not lines:
        return "", []

    header = lines[0].strip()
    body_lines = lines[1:]
    units: list[str] = []
    current: list[str] = []

    for raw_line in body_lines:
        stripped = raw_line.strip()
        if not stripped:
            if current and current[-1] != "":
                current.append("")
            continue

        if (CLAUSE_PATTERN.match(stripped) or LETTER_CLAUSE_PATTERN.match(stripped)) and current:
            units.append("\n".join(current).strip())
            current = [stripped]
            continue

        current.append(stripped)

    if current:
        units.append("\n".join(current).strip())

    if not units:
        body_text = "\n".join(line.strip() for line in body_lines if line.strip()).strip()
        return header, [body_text] if body_text else []

    return header, [unit for unit in units if unit]


def _build_breadcrumb(metadata: dict[str, object]) -> str:
    parts = [
        str(metadata.get("part_label") or "").strip(),
        str(metadata.get("chapter_label") or "").strip(),
        str(metadata.get("section_label") or "").strip(),
    ]
    return " | ".join(part for part in parts if part)


def _merge_units_with_header(header: str, units: list[str], max_chunk_chars: int) -> list[str]:
    if not header:
        return []
    if not units:
        return [header]

    chunks: list[str] = []
    current_units: list[str] = []

    def render(segment_units: list[str]) -> str:
        body = "\n\n".join(unit.strip() for unit in segment_units if unit.strip()).strip()
        return f"{header}\n\n{body}" if body else header

    for unit in units:
        candidate_units = current_units + [unit]
        candidate_text = render(candidate_units)
        if current_units and len(candidate_text) > max_chunk_chars:
            chunks.append(render(current_units))
            current_units = [unit]
        else:
            current_units = candidate_units

    if current_units:
        chunks.append(render(current_units))

    body_budget = max(200, max_chunk_chars - len(header) - 2)
    splitter = FixedSizeChunker(chunk_size=body_budget, overlap=min(120, max(40, body_budget // 8)))
    normalized_chunks: list[str] = []
    for chunk in chunks:
        if len(chunk) <= max_chunk_chars:
            normalized_chunks.append(chunk)
            continue
        body = chunk[len(header) :].strip()
        for sub_chunk in splitter.chunk(body):
            rendered = f"{header}\n\n{sub_chunk.strip()}" if sub_chunk.strip() else header
            normalized_chunks.append(rendered)

    return normalized_chunks


class ArticleChunker:
    """Simple article-based chunker for Vietnamese and English legal texts."""

    def chunk(self, text: str) -> list[str]:
        articles = extract_legal_articles(text)
        if articles:
            return [article["content"] for article in articles if str(article.get("content", "")).strip()]
        trimmed = trim_to_first_article(text)
        return [trimmed] if trimmed else []


class StructuredLegalChunker:
    """Split by article first, then split very long articles by clauses/paragraphs."""

    def __init__(self, max_chunk_chars: int = 1400) -> None:
        self.max_chunk_chars = max_chunk_chars

    def chunk(self, text: str) -> list[str]:
        return [chunk.content for chunk in self.chunk_records(text)]

    def chunk_records(self, text: str) -> list[LegalChunk]:
        article_records = extract_legal_articles(text)
        if not article_records:
            trimmed = trim_to_first_article(text)
            if not trimmed:
                return []
            return [
                LegalChunk(
                    content=trimmed,
                    metadata={
                        "article_number": "",
                        "article_title": "",
                        "part_label": "",
                        "chapter_label": "",
                        "section_label": "",
                        "segment_index": 0,
                        "segment_count": 1,
                    },
                )
            ]

        chunks: list[LegalChunk] = []
        for article_order, article in enumerate(article_records):
            header, units = _split_article_units(str(article["content"]))
            breadcrumb = _build_breadcrumb(article)
            effective_budget = max(300, self.max_chunk_chars - len(breadcrumb) - 1) if breadcrumb else self.max_chunk_chars
            chunk_texts = _merge_units_with_header(header, units, effective_budget)
            if not chunk_texts:
                chunk_texts = [str(article["content"]).strip()]

            for segment_index, chunk_text in enumerate(chunk_texts):
                content = chunk_text
                if breadcrumb:
                    content = f"{breadcrumb}\n{chunk_text}"
                chunks.append(
                    LegalChunk(
                        content=content.strip(),
                        metadata={
                            "part_label": article.get("part_label", ""),
                            "chapter_label": article.get("chapter_label", ""),
                            "section_label": article.get("section_label", ""),
                            "article_number": article.get("article_number", ""),
                            "article_title": article.get("article_title", ""),
                            "article_order": article_order,
                            "segment_index": segment_index,
                            "segment_count": len(chunk_texts),
                        },
                    )
                )
        return chunks


def infer_legal_metadata(path: Path, text: str | None = None) -> dict[str, object]:
    normalized_text = normalize_legal_text(text if text is not None else path.read_text(encoding="utf-8"))
    stem = path.stem
    stem_lower = stem.lower()

    domain = "Kh\u00e1c"
    for keyword, mapped_domain in DOMAIN_RULES:
        if keyword in stem_lower:
            domain = mapped_domain
            break

    year_match = YEAR_PATTERN.search(stem)
    year = int(year_match.group(0)) if year_match else None

    document_type = "code" if "b\u1ed9 lu\u1eadt" in stem_lower or "civil code" in stem_lower else "law"

    return {
        "source": f"data/{path.name}",
        "document_title": stem,
        "document_type": document_type,
        "domain": domain,
        "year": year,
        "language": detect_language(path, normalized_text),
        "jurisdiction": "Vietnam",
    }


def chunk_legal_text(
    text: str,
    strategy: str = "structured_legal",
    chunk_size: int = 1400,
    overlap: int = 150,
    max_sentences: int = 4,
) -> list[LegalChunk]:
    normalized = normalize_legal_text(text)
    trimmed = trim_to_first_article(normalized)

    if strategy in {"structured_legal", "legal", "articles"}:
        return StructuredLegalChunker(max_chunk_chars=chunk_size).chunk_records(normalized)

    if strategy in {"article_simple", "article"}:
        articles = extract_legal_articles(normalized)
        if articles:
            return [
                LegalChunk(
                    content=str(article["content"]).strip(),
                    metadata={
                        "part_label": article.get("part_label", ""),
                        "chapter_label": article.get("chapter_label", ""),
                        "section_label": article.get("section_label", ""),
                        "article_number": article.get("article_number", ""),
                        "article_title": article.get("article_title", ""),
                        "article_order": index,
                        "segment_index": 0,
                        "segment_count": 1,
                    },
                )
                for index, article in enumerate(articles)
                if str(article.get("content", "")).strip()
            ]
        return [LegalChunk(content=trimmed, metadata={})] if trimmed else []

    if strategy == "fixed":
        chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
        return [LegalChunk(content=chunk.strip(), metadata={}) for chunk in chunker.chunk(trimmed) if chunk.strip()]

    if strategy == "recursive":
        chunker = RecursiveChunker(chunk_size=chunk_size)
        return [LegalChunk(content=chunk.strip(), metadata={}) for chunk in chunker.chunk(trimmed) if chunk.strip()]

    if strategy in {"sentence", "sentences"}:
        chunker = SentenceChunker(max_sentences_per_chunk=max_sentences)
        return [LegalChunk(content=chunk.strip(), metadata={}) for chunk in chunker.chunk(trimmed) if chunk.strip()]

    raise ValueError(f"Unsupported legal chunking strategy: {strategy}")


def build_legal_chunk_documents(
    path: Path,
    max_chunks: int = 0,
    strategy: str = "structured_legal",
    chunk_size: int = 1400,
    overlap: int = 150,
    max_sentences: int = 4,
) -> list[Document]:
    text = path.read_text(encoding="utf-8")
    base_metadata = infer_legal_metadata(path, text=text)
    chunks = chunk_legal_text(
        text,
        strategy=strategy,
        chunk_size=chunk_size,
        overlap=overlap,
        max_sentences=max_sentences,
    )
    if max_chunks and max_chunks > 0:
        chunks = chunks[:max_chunks]

    documents: list[Document] = []
    for chunk_index, chunk in enumerate(chunks):
        article_number, article_title = parse_article_header(chunk.content)
        documents.append(
            Document(
                id=path.stem,
                content=chunk.content,
                metadata={
                    **base_metadata,
                    **chunk.metadata,
                    "chunk_index": chunk_index,
                    "char_length": len(chunk.content),
                    "article_number": chunk.metadata.get("article_number", article_number),
                    "article_title": chunk.metadata.get("article_title", article_title),
                    "chunking_strategy": strategy,
                },
            )
        )
    return documents


def is_legal_source_file(path: Path) -> bool:
    if path.suffix.lower() not in {".txt", ".md"}:
        return False

    name = path.stem.lower()
    legal_keywords = [
        "law",
        "lu\u1eadt",
        "b\u1ed9 lu\u1eadt",
        "planning",
        "press",
        "population",
        "investment",
        "marriage",
        "family",
        "educators",
        "children",
    ]
    return any(keyword in name for keyword in legal_keywords)


def collect_legal_source_files(data_dir: Path) -> list[Path]:
    return sorted(path for path in data_dir.iterdir() if path.is_file() and is_legal_source_file(path))
