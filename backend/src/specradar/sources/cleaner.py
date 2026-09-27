from __future__ import annotations

from html.parser import HTMLParser

from specradar.textutil import normalize_whitespace

_SKIP_TAGS = {"script", "style", "noscript", "head", "svg", "template"}
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
    parser = _TextExtractor()
    parser.feed(html)
    raw = parser.text()
    lines = [normalize_whitespace(line) for line in raw.splitlines()]
    return "\n".join(line for line in lines if line)


def clean_text(content: str, content_type: str) -> str:
    ctype = content_type.lower()
    if "html" in ctype:
        return clean_html(content)
    if "pdf" in ctype:
        raise NotImplementedError("PDF extraction not wired in MVP; pass extracted text")
    lines = [normalize_whitespace(line) for line in content.splitlines()]
    return "\n".join(line for line in lines if line)
