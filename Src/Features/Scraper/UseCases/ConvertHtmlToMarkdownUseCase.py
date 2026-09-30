"""
Module containing ConvertHtmlToMarkdownUseCase for extracting readable markdown from HTML.
"""

from typing import Optional
from bs4 import BeautifulSoup
import trafilatura
from markdownify import markdownify
from Src.Features.Scraper.Domain.CrawledPage import CrawledPage


class ConvertHtmlToMarkdownUseCase:
    """
    Extracts the primary readable content from raw HTML, converts it into clean Markdown,
    and constructs a CrawledPage domain entity.
    
    Invoked by:
    - CrawlWebsiteUseCase
    - Automated unit tests in test_convert_html_to_markdown.py
    """

    UNWANTED_TAGS = ["script", "style", "nav", "footer", "header", "noscript", "aside"]

    def execute(self, html_content: str, url: str, depth: int = 0) -> CrawledPage:
        """
        Converts the provided HTML string into a formatted CrawledPage entity.
        
        Invoked by:
        - CrawlWebsiteUseCase during page crawl processing.
        """
        if not html_content:
            return CrawledPage(
                url=url,
                title="Untitled",
                markdown_content="",
                character_count=0,
                depth=depth,
            )

        title = self._extract_page_title(html_content)
        cleaned_html = self._sanitize_html(html_content)
        extracted_markdown = self._extract_primary_content(cleaned_html)
        cleaned_markdown = extracted_markdown.strip()

        return CrawledPage(
            url=url,
            title=title,
            markdown_content=cleaned_markdown,
            character_count=len(cleaned_markdown),
            depth=depth,
        )

    def _sanitize_html(self, raw_html: str) -> str:
        soup = BeautifulSoup(raw_html, "lxml")
        for tag_name in self.UNWANTED_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        return str(soup)

    def _extract_page_title(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "lxml")
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.get_text():
            return h1_tag.get_text().strip()

        return "Untitled Page"

    def _extract_primary_content(self, cleaned_html: str) -> str:
        trafilatura_result = trafilatura.extract(
            cleaned_html,
            output_format="markdown",
            include_links=True,
            include_images=False,
            include_tables=True,
            include_formatting=True,
        )
        if trafilatura_result and len(trafilatura_result.strip()) > 30:
            return trafilatura_result

        return self._extract_fallback_markdown(cleaned_html)

    def _extract_fallback_markdown(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "lxml")
        target_container = (
            soup.find("main")
            or soup.find("article")
            or soup.find(attrs={"role": "main"})
            or soup.find(id="content")
            or soup.find(class_="content")
            or soup.body
            or soup
        )

        return markdownify(
            str(target_container),
            heading_style="ATX",
        )
