from __future__ import annotations

from specradar.sources.cleaner import clean_html, clean_text


def test_clean_html_strips_tags_and_noise() -> None:
    html = """
    <html><head><style>.x{color:red}</style></head>
    <body>
      <h1>Ranger Raptor</h1>
      <script>track();</script>
      <table><tr><td>Potência</td><td>397 cv</td></tr></table>
    </body></html>
    """
    text = clean_html(html)
    assert "397 cv" in text
    assert "Ranger Raptor" in text
    assert "track();" not in text
    assert "color:red" not in text


def test_block_tags_prevent_value_merge() -> None:
    html = "<li>397 cv</li><li>583 Nm</li>"
    text = clean_html(html)
    assert "397 cv583 Nm" not in text
    assert "397 cv" in text and "583 Nm" in text


def test_clean_text_plain_passthrough() -> None:
    assert clean_text("  Potência   397 cv  ", "text/plain") == "Potência 397 cv"
