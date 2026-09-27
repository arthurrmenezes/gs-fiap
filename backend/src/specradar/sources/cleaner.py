"""HTML/PDF → clean text. Pure and dependency-light (stdlib html.parser).

The cleaned text is what the LLM reads AND what the verifier checks evidence
against, so cleaning must be deterministic and preserve the literal spec wording.
"""

from __future__ import annotations

from html.parser import HTMLParser

from specradar.textutil import normalize_whitespace

# Tags whose text content is noise, never spec data.
_SKIP_TAGS = {"script", "style", "noscript", "head", "svg", "template"}
# Block tags that should introduce a newline so adjacent values do not merge.
_BLOCK_TAGS = {
    "p",
    "div",
    "li",
    "tr",
    "br",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "td",
    "th",
    "section",
    "article",
    "table",
    "ul",
    "ol",
    "dl",
    "dt",
    "dd",
}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


def clean_html(html: str) -> str:
    """Strip HTML to readable text, preserving spec wording and line structure."""
    parser = _TextExtractor()
    parser.feed(html)
    raw = parser.text()
    # Collapse intra-line whitespace per line, drop empty lines.
    lines = [normalize_whitespace(line) for line in raw.splitlines()]
    return "\n".join(line for line in lines if line)


def clean_text(content: str, content_type: str) -> str:
    """Dispatch cleaning by content type. Plain text passes through normalized."""
    ctype = content_type.lower()
    if "html" in ctype:
        return clean_html(content)
    if "pdf" in ctype:
        # PDF extraction (pdfminer/pypdf) is out of MVP scope for offline tests;
        # callers that fetch PDFs should pass already-extracted text here.
        raise NotImplementedError("PDF extraction not wired in MVP; pass extracted text")
    # treat as plain text
    lines = [normalize_whitespace(line) for line in content.splitlines()]
    return "\n".join(line for line in lines if line)
