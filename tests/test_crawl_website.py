"""
Integration tests for CrawlWebsiteUseCase.
"""

import pytest
import httpx
from Src.Features.Scraper.Domain.CrawlConfiguration import CrawlConfiguration
from Src.Features.Scraper.Domain.CrawlScopeMode import CrawlScopeMode
from Src.Features.Scraper.UseCases.CrawlWebsiteUseCase import CrawlWebsiteUseCase


@pytest.mark.asyncio
async def test_CrawlWebsite_WithStrictPrefix_CrawlsOnlySubpathAndRejectsExternalLinks(tmp_path):
    output_file = str(tmp_path / "test_docs.md")
    config = CrawlConfiguration(
        seed_url="https://site.com/docs",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
        output_destination=output_file,
        max_pages=10,
        delay_seconds=0.0,
    )

    page_seed = """
    <html>
        <head><title>Docs Root</title></head>
        <body>
            <h1>Welcome to Docs</h1>
            <a href="/docs/guide">Guide</a>
            <a href="/blog/news">Blog News</a>
            <a href="https://empik.com/store">Empik Store</a>
        </body>
    </html>
    """

    page_guide = """
    <html>
        <head><title>Guide Page</title></head>
        <body>
            <h1>Guide Details</h1>
            <p>Detailed steps in guide.</p>
            <a href="/docs/api">API Reference</a>
        </body>
    </html>
    """

    page_api = """
    <html>
        <head><title>API Reference</title></head>
        <body>
            <h1>API Specification</h1>
            <p>Endpoints and methods.</p>
        </body>
    </html>
    """

    def mock_handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if url_str in {"https://site.com/docs", "https://site.com/docs/"}:
            return httpx.Response(200, text=page_seed, headers={"content-type": "text/html"})
        if url_str in {"https://site.com/docs/guide", "https://site.com/docs/guide/"}:
            return httpx.Response(200, text=page_guide, headers={"content-type": "text/html"})
        if url_str in {"https://site.com/docs/api", "https://site.com/docs/api/"}:
            return httpx.Response(200, text=page_api, headers={"content-type": "text/html"})
        return httpx.Response(404, text="Not Found")

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as mock_client:
        use_case = CrawlWebsiteUseCase(config, client=mock_client)
        pages, statistics = await use_case.execute()

    crawled_urls = [p.url for p in pages]
    assert "https://site.com/docs" in crawled_urls
    assert "https://site.com/docs/guide" in crawled_urls
    assert "https://site.com/docs/api" in crawled_urls
    assert "https://site.com/blog/news" not in crawled_urls
    assert "https://empik.com/store" not in crawled_urls
    assert len(crawled_urls) == 3

    assert len(statistics.generated_files) == 1
    with open(statistics.generated_files[0], "r", encoding="utf-8") as file_handle:
        file_content = file_handle.read()

    assert "## Table of Contents" in file_content
    assert "Docs Root" in file_content
    assert "Guide Page" in file_content
    assert "API Reference" in file_content


@pytest.mark.asyncio
async def test_CrawlWebsite_WithCircularAndSelfReferencingLinks_VisitsEachPageExactlyOnce(tmp_path):
    output_file = str(tmp_path / "circular_docs.md")
    config = CrawlConfiguration(
        seed_url="https://site.com/docs/page-a",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
        path_prefix="/docs",
        output_destination=output_file,
        max_pages=20,
        delay_seconds=0.0,
    )

    page_a = """
    <html>
        <head><title>Page A</title></head>
        <body>
            <h1>Page A Content</h1>
            <a href="/docs/page-b">Go to B</a>
            <a href="/docs/page-a">Self reference to A</a>
        </body>
    </html>
    """

    page_b = """
    <html>
        <head><title>Page B</title></head>
        <body>
            <h1>Page B Content</h1>
            <a href="/docs/page-a">Go back to A (Cycle)</a>
            <a href="/docs/page-b">Self reference to B</a>
        </body>
    </html>
    """

    def mock_handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if url_str in {"https://site.com/docs/page-a", "https://site.com/docs/page-a/"}:
            return httpx.Response(200, text=page_a, headers={"content-type": "text/html"})
        if url_str in {"https://site.com/docs/page-b", "https://site.com/docs/page-b/"}:
            return httpx.Response(200, text=page_b, headers={"content-type": "text/html"})
        return httpx.Response(404, text="Not Found")

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as mock_client:
        use_case = CrawlWebsiteUseCase(config, client=mock_client)
        pages, statistics = await use_case.execute()

    crawled_urls = [p.url for p in pages]
    assert len(crawled_urls) == 2
    assert "https://site.com/docs/page-a" in crawled_urls
    assert "https://site.com/docs/page-b" in crawled_urls
    assert statistics.crawled_pages_count == 2


@pytest.mark.asyncio
async def test_CrawlWebsite_WithReviewCallbackExcludingUrls_CompilesOnlyApprovedPages(tmp_path):
    output_file = str(tmp_path / "reviewed_docs.md")
    config = CrawlConfiguration(
        seed_url="https://site.com/docs",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
        output_destination=output_file,
        max_pages=10,
        delay_seconds=0.0,
        enable_review=True,
    )

    page_seed = """
    <html>
        <body>
            <h1>Seed Page</h1>
            <a href="/docs/keep1">Keep 1</a>
            <a href="/docs/kula/remove">Remove Me</a>
        </body>
    </html>
    """

    page_keep = "<html><body><h1>Keep 1 Page</h1></body></html>"
    page_remove = "<html><body><h1>Excluded Page</h1></body></html>"

    def mock_handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if url_str in {"https://site.com/docs", "https://site.com/docs/"}:
            return httpx.Response(200, text=page_seed, headers={"content-type": "text/html"})
        if url_str == "https://site.com/docs/keep1":
            return httpx.Response(200, text=page_keep, headers={"content-type": "text/html"})
        if url_str == "https://site.com/docs/kula/remove":
            return httpx.Response(200, text=page_remove, headers={"content-type": "text/html"})
        return httpx.Response(404, text="Not Found")

    def simulate_user_review(discovered_urls, exclusions_manager):
        exclusions_manager.add_exclusion("/docs/kula")
        return exclusions_manager.filter_urls(discovered_urls)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as mock_client:
        use_case = CrawlWebsiteUseCase(
            configuration=config,
            review_callback=simulate_user_review,
            client=mock_client,
        )
        pages, statistics = await use_case.execute()

    compiled_urls = [p.url for p in pages]
    assert "https://site.com/docs" in compiled_urls
    assert "https://site.com/docs/keep1" in compiled_urls
    assert "https://site.com/docs/kula/remove" not in compiled_urls
    assert len(compiled_urls) == 2

    with open(statistics.generated_files[0], "r", encoding="utf-8") as file_handle:
        content = file_handle.read()

    assert "Keep 1 Page" in content
    assert "Excluded Page" not in content

