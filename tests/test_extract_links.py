"""
Unit tests for ExtractLinksUseCase.
"""

from Src.Features.Scraper.UseCases.ExtractLinksUseCase import ExtractLinksUseCase


def test_ExtractLinks_WithHtmlSnippet_ReturnsAbsoluteUrls():
    use_case = ExtractLinksUseCase()
    html = """
    <html>
        <body>
            <a href="/buka/page1">Page 1</a>
            <a href="https://amazon.com/buka/page2">Page 2</a>
            <a href="nested/item">Nested</a>
        </body>
    </html>
    """
    base_url = "https://amazon.com/buka/"
    links = use_case.execute(html, base_url)

    assert "https://amazon.com/buka/page1" in links
    assert "https://amazon.com/buka/page2" in links
    assert "https://amazon.com/buka/nested/item" in links


def test_ExtractLinks_WithRelativeAndFragmentLinks_FiltersAndResolvesCorrectly():
    use_case = ExtractLinksUseCase()
    html = """
    <html>
        <body>
            <a href="#section-top">Jump</a>
            <a href="javascript:alert(1)">JS</a>
            <a href="mailto:test@example.com">Email</a>
            <a href="/buka/valid">Valid</a>
        </body>
    </html>
    """
    base_url = "https://amazon.com/buka"
    links = use_case.execute(html, base_url)

    assert links == {"https://amazon.com/buka/valid"}


def test_ExtractLinks_WithEmptyOrNoneHtml_ReturnsEmptySet():
    use_case = ExtractLinksUseCase()
    assert use_case.execute("", "https://amazon.com/buka") == set()
