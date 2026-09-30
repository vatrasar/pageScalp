"""
Unit tests for ConvertHtmlToMarkdownUseCase.
"""

from Src.Features.Scraper.UseCases.ConvertHtmlToMarkdownUseCase import ConvertHtmlToMarkdownUseCase


def test_ConvertHtmlToMarkdown_WithArticleHtml_ExtractsTitleAndMarkdown():
    use_case = ConvertHtmlToMarkdownUseCase()
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>My Great Documentation</title>
        </head>
        <body>
            <main>
                <h1>Welcome to PageScalp</h1>
                <p>This is a paragraph explaining the crawler tool.</p>
                <pre><code>def example(): return 42</code></pre>
            </main>
        </body>
    </html>
    """
    url = "https://example.com/buka/intro"
    page = use_case.execute(html, url)

    assert page.url == url
    assert page.title == "My Great Documentation"
    assert "PageScalp" in page.markdown_content
    assert "crawler tool" in page.markdown_content
    assert page.character_count > 0


def test_ConvertHtmlToMarkdown_WithBoilerplateNavAndFooter_StripsBoilerplate():
    use_case = ConvertHtmlToMarkdownUseCase()
    html = """
    <html>
        <head><title>Clean Content Test</title></head>
        <body>
            <nav><a href="/home">Home Menu Item</a><a href="/login">Login Menu Item</a></nav>
            <article>
                <h2>Subheading Test</h2>
                <p>Essential documentation body content.</p>
            </article>
            <footer>Copyright 2026 Secret Footer Company</footer>
        </body>
    </html>
    """
    url = "https://example.com/buka/clean"
    page = use_case.execute(html, url)

    assert "Subheading Test" in page.markdown_content
    assert "Essential documentation body content" in page.markdown_content
    assert "Login Menu Item" not in page.markdown_content
    assert "Secret Footer Company" not in page.markdown_content


def test_ConvertHtmlToMarkdown_WithEmptyHtml_ReturnsEmptyCrawledPage():
    use_case = ConvertHtmlToMarkdownUseCase()
    page = use_case.execute("", "https://example.com/buka/empty")

    assert page.url == "https://example.com/buka/empty"
    assert page.title == "Untitled"
    assert page.character_count == 0
